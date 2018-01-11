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
        project = self._apply_config_key(project, 'project', ProjectOptions)
        github_user = self._apply_config_key(github_user, 'github_user',
                                             GitHubUser)

        super(ReleaseNoteWriter, self).__init__(project, github_user)
        self._latest_release_tag = None
        self._latest_release_tag_name = None
        self._latest_release_commit_date = None

    def _apply_config_key(self, var, key, obj_cls):
        # this is to make codeclimate happy
        if var is None and key in self.config.keys():
            var = obj_cls(**self.config[key])
        return var

    def filter_recent_pulls(self, pulls, since):
        # filter for date
        pulls = [p for p in pulls if p['merged_at'] > since]
        # ensure that you don't have the last PR from previous showing up
        # (there can be a second in time difference between commit and
        # merge)
        latest_tag_sha = self._latest_release_tag['commit']['sha']
        pulls = [p for p in pulls
                 if p['merge_commit_sha'] != latest_tag_sha]
        return pulls

    def label_organized_merged_pulls(self, since=''):
        # the implementation challenge is that the return info from pulls
        # doesn't currently include info about labels -- that is contains in
        # the return info from issues (all pulls are issues).
        params = {'state': 'closed'}
        if since != '':
            params.update({'since': since})

        recent_pulls = self.api_get("pulls", params=params).json()
        recent_pulls = self.filter_recent_pulls(recent_pulls, since)
        recent_issues = self.api_get("issues", params=params).json()
        issues_by_number = {iss['number']: iss for iss in recent_issues}
        desired_pulls = collections.defaultdict(list)
        for pull in recent_pulls:
            issue = issues_by_number[pull['number']]
            label_names = [label['name'] for label in issue['labels']]
            for label in label_names:
                desired_pulls[label] += [pull]
            if not label_names:
                desired_pulls[None] += [pull]

        return desired_pulls

    def _latest_release_tag_info(self, tag_name):
        tags = self.api_get("tags").json()
        desired_tag_list = [t for t in self.api_get("tags").json()
                            if t['name'] == tag_name]
        assert len(desired_tag_list) == 1
        self._latest_release_tag = desired_tag_list[0]

    @property
    def latest_release_commit_date(self):
        # note that we use the date of the commit of the last release, not
        # the date of the release itself (can release long after the commit)
        latest_release =  self.api_get("releases/latest").json()
        if self._latest_release_tag_name != latest_release['tag_name']:
            self._latest_release_tag_info(latest_release['tag_name'])
            latest_tag_commit_sha = \
                self._latest_release_tag['commit']['sha']
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

    @staticmethod
    def _pull_to_labels(pull_dict):
        pull_to_labels = collections.defaultdict(list)
        for label in pull_dict:
            for pull in pull_dict[label]:
                pull_to_labels[pull['number']] += [label]
        return pull_to_labels

    def release_notes_from_pulls(self, pull_dict):
        out_str = ""
        label_categories = [lbl['label'] for lbl in self.config['labels']]
        unknown_labels = set(pull_dict) - set(label_categories)
        pull_to_labels = self._pull_to_labels(pull_dict)

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

