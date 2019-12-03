import argparse
from autorelease.github_release import \
        GitHubUser, GitHubRepoBase, ProjectOptions

class Authenticate(GitHubRepoBase):
    def check(self):
        # load tags to see if API calls work
        result = self.api_get("tags")
        if not result.ok:
            raise ValueError("Bad authentication")


def make_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--token', type=str, help='authorization token')
    parser.add_argument('--repo', type=str)
    parser.add_argument('--user', type=str, help='GitHub username')
    parser.add_argument('--repo-owner', type=str, default=None)
    parser.add_argument('--project_name', type=str, default=None)
    return parser


def main():
    parser = make_parser()
    opts = parser.parse_args()
    if opts.repo_owner is None:
        opts.repo_owner = opts.user
    if opts.project_name is None:
        opts.project_name = opts.repo
    github_user = GitHubUser(opts.user, opts.token)
    project = ProjectOptions(repo_owner=opts.repo_owner,
                             repo_name=opts.repo,
                             project_name=opts.project_name)
    auth = Authenticate(project, github_user)
    auth.check()


if __name__ == "__main__":
    main()

