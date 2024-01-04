from .query_runner import QueryRunner

import typing
import enum
import datetime

from .utils import string_to_datetime



class PRStatus(enum.Enum):
    OPEN = "open"
    CLOSED = "closed"
    MERGED = "merged"


class PR(typing.NamedTuple):
    number: int
    target: str
    title: str
    status: PRStatus
    author: str
    labels: typing.List[str]
    url: str
    merge_time: typing.Optional[datetime.datetime]

    @classmethod
    def from_api_response(cls, api_pr):
        return cls(
            number=int(api_pr["number"]),
            target=api_pr["baseRefName"],
            title=api_pr["title"],
            status=getattr(PRStatus, api_pr["state"]),
            author=api_pr["author"]["login"],
            labels=[node["name"] for node in api_pr["labels"]["nodes"]],
            url=api_pr["url"],
            merge_time=string_to_datetime(api_pr["mergedAt"]),
        )

PR_QUERY = """
{
  repository(name: "$repo_name", owner: "$repo_owner") {
    pullRequests(
      orderBy: {field: UPDATED_AT, direction: DESC}
      first: 100
      $after
      states: MERGED
      baseRefName: "$target_branch"
    ) {
      nodes {
        author {
          login
        }
        merged
        mergedAt
        number
        title
        headRefName
        closed
        baseRefName
        state
        url
        labels(first: 100) {
          nodes {
            name
          }
          pageInfo {
            endCursor
            hasNextPage
            startCursor
          }
        }
      }
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
    }
  }
}
"""

def graphql_get_all_prs(owner, repo, auth, target_branch):
    # TODO: query needs to take repo and owner
    def extractor(result):
        return result["data"]["repository"]["pullRequests"]["nodes"]

    def next_page_cursor(result):
        info = result["data"]["repository"]["pullRequests"]["pageInfo"]
        next_cursor = info["endCursor"] if info["hasNextPage"] else None
        return next_cursor


    query_runner = QueryRunner(PR_QUERY, auth=auth,
                               api_endpoint="https://api.github.com/graphql")
    extracted_results = []

    # TODO: how to manage nested inner loops?
    # actually.. better choice is to post-process to remove inner
    # paginations: get additional labels for anything with more than 100
    # labels
    default_kwargs = {
        'repo_owner': owner,
        'repo_name': repo,
        'target_branch': target_branch,
    }
    result = query_runner(after="", **default_kwargs)
    extracted_results.extend(extractor(result))
    while cursor := next_page_cursor(result):
        result = query_runner(after=f'after: "{cursor}"', **default_kwargs)
        extracted_results.extend(extractor(result))

    return extracted_results


