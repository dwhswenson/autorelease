from typing import NamedTuple
from .query_runner import QueryRunner
from .utils import string_to_datetime
import datetime

class Release(NamedTuple):
    name: str
    tag: str
    draft: bool
    prerelease: bool
    latest: bool
    date: datetime.datetime

    @classmethod
    def from_api(cls, api_release):
        return cls(
            name=api_release['name'],
            tag=api_release["tagName"],
            draft=api_release["isDraft"],
            prerelease=api_release["isPrerelease"],
            latest=api_release["isLatest"],
            date=string_to_datetime(api_release["publishedAt"]),
        )

RELEASES_QUERY = """
{
  repository(name: "$repo_name", owner: "$repo_owner") {
    releases(orderBy: {field: CREATED_AT, direction: DESC}, first: 100) {
      nodes {
        publishedAt
        isLatest
        isPrerelease
        isDraft
        name
        tagName
      }
    }
  }
}
"""

def latest_release(owner, repo, auth):
    # TODO: support paginated releases
    runner = QueryRunner(RELEASES_QUERY, auth)
    result = runner(repo_name=repo, repo_owner=owner)
    api_release_info = result['data']['repository']['releases']['nodes']
    releases = [Release.from_api(rel) for rel in api_release_info]
    claim_latest = [rel for rel in releases if rel.latest]
    assert len(claim_latest) == 1
    return claim_latest[0]
