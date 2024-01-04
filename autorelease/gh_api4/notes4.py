"""
Writing release notes based on the GitHub v4 (GraphQL) API
"""

import typing
import enum
import datetime

from .pull_requests import PRStatus, PR, graphql_get_all_prs
from .releases import latest_release

import logging
_logger = logging.getLogger(__name__)

def filter_release_prs(all_prs, prev_release_date, target_branch="main"):
    def is_release_pr(pr):
        return (
            pr.status == PRStatus.MERGED
            and pr.merge_time > prev_release_date
            and pr.target == target_branch
        )

    for pr in all_prs:
        _logger.info(f"{pr}")
        if is_release_pr(pr):
            _logger.info(f"Including {pr}")
            yield pr
        else:
            _logger.info("Skipping")


def prs_since_latest_release(owner, repo, auth, target_branch="main"):
    latest = latest_release(owner, repo, auth)
    _logger.info(f"Latest release: {latest}")

    release_date = latest.date
    all_prs = [PR.from_api_response(pr)
               for pr in graphql_get_all_prs(owner, repo, auth,
                                             target_branch)]

    _logger.info(f"Loaded {len(all_prs)} PRs")
    new_prs = list(filter_release_prs(
        all_prs=all_prs,
        prev_release_date=latest.date,
        target_branch=target_branch
    ))
    _logger.info(f"After filtering, found {len(new_prs)} new PRs")
    return new_prs


class PRCategory:
    def __init__(self, label, heading, topics):
        self.label = label
        self.heading = heading
        self.topics = topics
        self.prs = []
        self.topic_prs = {l: [] for l in topics}

    def append(self, pr):
        if topics := set(pr.labels) & set(self.topics):
            for topic in topics:
                self.topic_prs[topic].append(pr)
        else:
            self.prs.append(pr)


class NotesWriter:
    def __init__(self, category_labels, topics, standard_contributors):
        self.category_labels = category_labels
        self.topics = topics
        self.standard_contributors = set(standard_contributors)

    @staticmethod
    def assign_prs_to_categories(prs, categories):
        category_labels = set(categories)
        for pr in prs:
            selected = [categories[label]
                        for label in set(pr.labels) & category_labels]

            if not selected:
                selected = [categories[None]]

            for category in selected:
                category.append(pr)

    def _write_pr_details(self, pr, category_label, topic_label):
        out = f"[#{pr.number}]({pr.url})"
        if pr.author not in self.standard_contributors:
            out += f" @{pr.author}"

        out_labels = [label for label in pr.labels
                      if label not in {category_label, topic_label}]
        if out_labels:
            out += " "
        out += " ".join(f"#{label}" for label in out_labels)
        return out

    def write_single_pr(self, pr, category_label):
        details = self._write_pr_details(pr, category_label, "")
        out = f"* {pr.title} ({details})\n"
        return out

    def write_topic(self, category, topic):
        out = ""
        topic_prs = category.topic_prs[topic]
        topic_text = category.topics[topic]
        if len(topic_prs):
            out += f"* {topic_text} ("
            out += ", ".join(
                self._write_pr_details(pr, category.label, topic)
                for pr in topic_prs
            )
            out += ")\n"

        return out

    def write_category(self, category):
        out = f"## {category.heading}\n\n"
        for pr in category.prs:
            out += self.write_single_pr(pr, category.label)

        for topic in category.topics:
            out += self.write_topic(category, topic)

        return out

    def write(self, prs):
        categories = {
            label: PRCategory(label, heading, self.topics.get(label, {}))
            for label, heading in self.category_labels.items()
        }
        categories[None] = PRCategory(None, "Unlabeled PRs", {})
        self.assign_prs_to_categories(prs, categories)

        out = "\n".join(self.write_category(category)
                        for category in categories.values())
        return out
