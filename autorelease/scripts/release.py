#!/usr/bin/env python
from __future__ import print_function
import argparse
import logging
import re
import git

from autorelease import GitHubReleaser, GitHubUser, ProjectOptions

def make_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--token', type=str, help='authorization token')
    parser.add_argument('--project_name', type=str)
    parser.add_argument('--version', type=str)
    parser.add_argument('--user', type=str, help='GitHub username')
    parser.add_argument('--repo', type=str, default='.')
    parser.add_argument('--repo_owner', type=str)
    parser.add_argument('--repo_name', type=str)
    parser.add_argument('--dry', action='store_true')
    parser.add_argument('-q', '--quiet', action='store_true')
    return parser

# move this to scripts/utils?
def make_logger(quiet=False):
    pass

def github_url_to_owner_repo(url):
    pattern = ".*github.com[\:\/]([^\/]+)\/(.*)\.git"
    match = re.match(pattern, url)
    return match.groups()

def main():
    parser = make_parser()
    opts = parser.parse_args()

    logger = make_logger(opts.quiet)

    print(opts)

    repo = git.Repo(opts.repo)

    upstream = [r for r in repo.remotes if r.name == 'upstream']
    origin = [r for r in repo.remotes if r.name == 'origin']
    if not upstream:
        upstream = origin

    if upstream == origin == []:
        raise RuntimeError("Can't guess data for this repository")

    assert len(upstream) == len(origin) == 1
    upstream = upstream[0]
    origin = origin[0]

    (owner, name) = github_url_to_owner_repo(upstream.url)
    (user, _) = github_url_to_owner_repo(origin.url)

    if opts.repo_owner is not None:
        owner = opts.repo_owner
    if opts.repo_name is not None:
        name = opts.repo_name
    if opts.user is not None:
        user = opts.user

    github_user = GitHubUser(user, opts.token)
    project = ProjectOptions(owner, name, opts.project_name)
    releaser = GitHubReleaser(
        project=project,
        version=opts.version,
        repo=repo,
        github_user=github_user
    )
    
    # testing
    expected_pr = releaser.find_relevant_pr()
    print("Expected PR: " + str(expected_pr))
    print("PR issue: " + str(releaser.get_pr_data(expected_pr)))
    print("POST DATA:")
    print(releaser.generate_post_data())
    if not opts.dry:
        releaser.create_release()

if __name__ == "__main__":
    main()
