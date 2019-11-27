import re
import json

import requests
import git

from collections import namedtuple

ProjectOptions = namedtuple('ProjectOptions', ['repo_owner',
                                               'repo_name',
                                               'project_name'])

class GitHubUser(namedtuple('GitHubUser', ['username', 'token'])):
    @property
    def auth(self):
        return (self.username, self.token)

class GitHubRepoBase(object):
    """
    Parameters
    ----------
    project: :class:`.ProjectOptions`
    github_user: :class:`.GitHubUser`
    """
    def __init__(self, project, github_user):
        github_api_url = "https://api.github.com/"
        self.project = project
        self.repo_api_url = (github_api_url + "repos/" + project.repo_owner
                             + "/" + project.repo_name + "/")
        self.github_user = github_user

    def api_get(self, url_ending, params=None):
        return requests.get(url=self.repo_api_url + url_ending,
                            params=params,
                            auth=self.github_user.auth)

    def api_get_json_all(self, url_ending, params=None):
        # only for issues, which limit to 30 per return
        my_params = {}
        my_params.update(params)
        my_params.update({'sort': 'updated', 'direction': 'asc'})
        results = {}  # we use a dict to easily look up by number
        # actual return is list of values
        should_continue = True
        while should_continue:
            local_results_req = self.api_get(url_ending, my_params)
            local_results = local_results_req.json()
            if local_results:
                since = local_results[-1]['updated_at']
                # print(local_results[-1]['updated_at'],
                      # local_results[0]['updated_at'])
                my_params['since'] = since
            local_result_dict = {result['number']: result
                                 for result in local_results
                                 if result['number'] not in results}
            results.update(local_result_dict)
            should_continue = local_result_dict
            # print(results.keys())
        return list(results.values())


class GitHubReleaser(GitHubRepoBase):
    """
    Parameters
    ----------
    project : :class:`.ProjectOptions`
    version : str or :class:`packaging.versions.Version`
    repo : :class:`git.Repo`
    github_user : :class:`.GitHubUser`

    Attributes
    ----------
    release_target_commitish : str
    """
    def __init__(self, project, version, repo, github_user):
        super(GitHubReleaser, self).__init__(project, github_user)
        self.version = version
        # pr_re set in pr_pattern
        self._pr_pattern = None
        self.pr_re = None
        self.repo = repo

        self.pr_pattern = "Merge pull request #([0-9]+)"
        self.release_target_commitish = "stable"

    # THINGS YOU MIGHT WANT TO OVERRIDE
    @property
    def release_name(self):
        return self.project.project_name + " " + str(self.version)

    @property
    def tag_name(self):
        return "v" + str(self.version)

    def extract_release_notes(self, text):
        # TODO: make this more complicated
        return text

    # THINGS YOU'RE LESS LIKELY TO OVERRIDE
    @property
    def pr_pattern(self):
        return self._pr_pattern

    @pr_pattern.setter
    def pr_pattern(self, value):
        self._pr_pattern = value
        self.pr_re = re.compile(self._pr_pattern)

    def find_relevant_pr(self):
        # this uses the git log to find the most recent merge from PR
        # (assuming certain text in the commit log for PR merges)
        found = False
        commits = self.repo.iter_commits(self.release_target_commitish)
        commit = next(commits)
        while commit and not found:
            match = self.pr_re.match(commit.message)
            if match is not None:
                found = True
                pr_number = match.group(1)  # don't like hardcoded 1
            else:
                commit = next(commits)
        return int(pr_number)

    def get_pr_data(self, pr_number):
        pr_url = self.repo_api_url + "issues/" + str(pr_number)
        pr_data = requests.get(pr_url, auth=self.github_user.auth).json()
        return pr_data

    def generate_post_data(self, draft=False, prerelease=False):
        pr_number = self.find_relevant_pr()
        pr_data = self.get_pr_data(pr_number)
        pr_body = pr_data['body']
        release_notes = self.extract_release_notes(pr_body)
        post_data = {
            'tag_name': self.tag_name,
            'target_commitish': self.release_target_commitish,
            'name': self.release_name,
            'body': release_notes,
            'draft': draft,
            'prerelease': prerelease
        }
        return post_data

    def create_release(self, draft=False, prerelease=False):
        post_data = json.dumps(self.generate_post_data())
        post_status = requests.post(self.repo_api_url + "releases",
                                    data=post_data,
                                    auth=self.github_user.auth)
