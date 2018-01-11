#!/usr/bin/env python
from __future__ import print_function
import sys
import collections
import yaml
import requests

from .github_release import GitHubRepoBase, GitHubUser, ProjectOptions

class ReleaseNoteWriter(GitHubRepoBase):
    def __init__(self, config, project=None, github_user=None):
        if isinstance(config, str):
            with open(config) as f:
                config = yaml.load(f.read())

        self.config = config
        if project is None and 'project' in config.keys():
            project = ProjectOptions(**config['project'])
        if github_user is None and 'github_user' in config.keys():
            github_user = GitHubUser(**config['github_user'])

        super(ReleaseNoteWriter, self).__init__(project, github_user)
        self._latest_release_tag_name = None
        self._latest_release_commit_date = None

    def label_organized_merged_pulls(self, since=None):
        # the implementation challenge is that the return info from pulls
        # doesn't currently include info about labels -- that is contains in
        # the return info from issues (all pulls are issues).
        params = {'state': 'closed'}
        if since is not None:
            params.update({'since': since})

        recent_pulls = self.api_get("pulls", params=params).json()
        recent_issues = self.api_get("issues", params=params).json()
        issues_by_number = {iss['number']: iss for iss in recent_issues}
        desired_pulls = collections.defaultdict(list)
        for pull in recent_pulls:
            merge_date = pull['merged_at']
            if merge_date and since and merge_date > since:
                issue = issues_by_number[pull['number']]
                label_names = [label['name'] for label in issue['labels']]
                for label in label_names:
                    desired_pulls[label] += [pull]
                if not label_names:
                    desired_pulls[None] += [pull]

        return desired_pulls

    @property
    def latest_release_commit_date(self):
        # note that we use the date of the commit of the last release, not
        # the date of the release itself (can release long after the commit)
        latest_release =  self.api_get("releases/latest").json()
        if self._latest_release_tag_name != latest_release['tag_name']:
            tags = self.api_get("tags").json()
            desired_tag_list = [t for t in self.api_get("tags").json()
                                if t['name'] == latest_release['tag_name']]
            assert len(desired_tag_list) == 1
            latest_tag_commit_sha = desired_tag_list[0]['commit']['sha']
            commit = self.api_get("commits/" + latest_tag_commit_sha).json()
            self._latest_release_commit_date = \
                    commit['commit']['committer']['date']
            self._latest_release_tag_name = latest_release['tag_name']
        return self._latest_release_commit_date

    def write_pull_line(self, pull, extra_labels=None):
        if extra_labels is None:
            extra_labels = []
        title = pull['title']
        number = str(pull['number'])
        author = pull['user']['login']
        out_str = "* " + title + " (#" + number + ")"
        if author not in self.config['standard_contributors']:
            out_str += " @" + author
        for label in extra_labels:
            out_str += " #" + label
        out_str += "\n"
        return out_str

    def release_notes_from_pulls(self, pull_dict):
        out_str = ""
        label_categories = [lbl['label'] for lbl in self.config['labels']]
        unknown_labels = set(pull_dict) - set(label_categories)
        pull_to_labels = collections.defaultdict(list)
        for label in pull_dict:
            for pull in pull_dict[label]:
                pull_to_labels[pull['number']] += [label]

        treated_pulls = []

        for lbl in self.config['labels']:
            label = lbl['label']
            out_str += "\n# " + lbl['heading'] + "\n"
            for pull in pull_dict[label]:
                pull_labels = set(pull_to_labels[pull['number']])
                extra_labels = pull_labels - set([label])
                out_str += self.write_pull_line(pull, extra_labels)
                treated_pulls.append(pull['number'])

        if len(treated_pulls) != len(pull_to_labels):
            out_str += "\n-----\n\n# Pulls with unknown labels\n"

        for label in unknown_labels:
            untreated = [pull for pull in pull_dict[label]
                         if pull['number'] not in treated_pulls]
            if untreated:
                out_str += "\n## " + str(label) + "\n"
            for pull in untreated:
                out_str += self.write_pull_line(pull)
                treated_pulls.append(pull['number'])

        return out_str

    def write_release_notes(self, outfile=None):
        if outfile is None:
            outfile = sys.stdout
        elif isinstance(outfile, str):
            outfile = open(outfile)
        release_date = self.latest_release_commit_date
        pull_dict = self.label_organized_merged_pulls(since=release_date)
        notes = self.release_notes_from_pulls(pull_dict)
        outfile.write(notes)
        outfile.flush()
        if outfile != sys.stdout:
            outfile.close()

