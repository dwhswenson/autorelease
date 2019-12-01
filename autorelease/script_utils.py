import argparse
import git

from .utils import github_url_to_owner_repo

from autorelease import GitHubUser, ProjectOptions

class AutoreleaseParsingHelper(object):
    def __init__(self, parser=None, disable_defaults=False):
        if parser is None:
            parser = argparse.ArgumentParser()
        self.parser = parser
        self.parser.add_argument('-q', '--quiet', action='store_true')

        self.make_objects = []

    def add_github_parsing(self):
        self.parser.add_argument('-u', '--username', type=str,
                                 help='GitHub username')
        self.parser.add_argument('--token', type=str,
                                 help='authorization token')
        self.make_objects.append(GitHubUser)

    def add_project_parsing(self):
        self.parser.add_argument('--repo_owner', type=str)
        self.parser.add_argument('--repo_name', type=str)
        self.parser.add_argument('--project_name', type=str)
        self.make_objects.append(ProjectOptions)

    def add_repo_parsing(self):
        self.parser.add_argument('--repo', type=str, default='.')

    def parse_args(self, args=None):
        opts = self.parser.parse_args(args=args)
        return AutoreleaseParsedArguments(opts, self.make_objects)


class AutoreleaseParsedArguments(object):
    def __init__(self, opts, make_objects):
        self.opts = opts
        self.make_objects = make_objects

        self._upstream = None
        self._origin = None
        self._github_user = None
        self._project = None
        self._repo = None

    def __getattr__(self, name):
        return getattr(self.opts, name)

    def _remotes(self, internal):
        if internal is None and self.repo is not None:
            self.set_upstream_origin()

    @property
    def upstream(self):
        self._remotes(self._upstream)
        return self._upstream

    @property
    def origin(self):
        self._remotes(self._origin)
        return self._origin

    def set_upstream_origin(self, repo=None):
        if repo is None:
            repo = self.repo
        # input is git.Repo object
        upstream = [r for r in repo.remotes if r.name == 'upstream']
        origin = [r for r in repo.remotes if r.name == 'origin']
        if not upstream:
            upstream = origin

        if upstream == origin == []:
            raise RuntimeError("Can't guess data for this repository")

        assert len(upstream) == len(origin) == 1
        self.upstream = upstream[0]
        self.origin = origin[0]

    def guess_project(self):
        guess = {k: None
                 for k in ['repo_owner', 'repo_name', 'project_name']}
        if self.repo is not None:
            (owner, name) = github_url_to_owner_repo(self.upstream.url)
            guess = {'repo_owner': owner,
                     'repo_name': name,
                     'project_name': name}
        return guess

    def guess_github_user(self):
        guess = {k: None for k in ['username', 'token']}
        if self.repo is not None:
            (user, _) = github_url_to_owner_repo(self.origin.url)
            guess.update({'username': user})
        return guess

    @property
    def repo(self):
        if self._repo is None and hasattr(self.opts, 'repo'):
            self._repo = git.Repo(self.opts.repo)
        return self._repo

    @property
    def github_user(self):
        if self._github_user is None and GitHubUser in self.make_objects:
            self._github_user = self._make_object(GitHubUser,
                                                  self.guess_github_user,
                                                  opts=self.opts)
        return self._github_user

    @property
    def project(self):
        if self._project is None and ProjectOptions in self.make_objects:
            self._project = self._make_object(ProjectOptions,
                                              self.guess_project,
                                              self.opts)
        return self._project


    @staticmethod
    def _make_object(obj_cls, guesser, opts):
        # here's an abstract function....
        if opts is None:
            raise RuntimeError(
                "Can't retrieve object before parsing arguments. "
                + "Run AutoreleaseParsingHelper.parse_args() first.")
        kwargs = guesser()
        opts_dct = vars(opts)
        kwargs_opts = {k: opts_dct[k] for k in kwargs
                       if opts_dct[k] is not None}
        kwargs.update(kwargs_opts)
        kwargs = {k: v for (k, v) in kwargs.items() if v is not None}
        try:
            return obj_cls(**kwargs)
        except TypeError:
            return None
        # alternate: this is stricter and requires all values non-None
        #if any([v is None for v in kwargs.values()]):
            #return None
        #else:
            #return obj_cls(**kwargs)
