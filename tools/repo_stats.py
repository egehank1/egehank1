#!/usr/bin/env python3
"""Print a small summary of a GitHub user's public repositories.

Uses the GitHub REST API (https://docs.github.com/en/rest). No token is
required for public data; set GITHUB_TOKEN to raise the rate limit.

Usage:
    python tools/repo_stats.py            # defaults to egehank1
    python tools/repo_stats.py <username> # any public account
"""

import json
import os
import sys
import urllib.request
from collections import Counter

API = "https://api.github.com"


def get(path: str):
    request = urllib.request.Request(
        f"{API}{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "repo-stats-script",
        },
    )
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def public_repos(user: str):
    page = 1
    while True:
        batch = get(f"/users/{user}/repos?per_page=100&page={page}&type=owner")
        if not batch:
            return
        yield from batch
        page += 1


def main() -> int:
    user = sys.argv[1] if len(sys.argv) > 1 else "egehank1"
    repos = [repo for repo in public_repos(user) if not repo["fork"]]
    languages = Counter(repo["language"] for repo in repos if repo["language"])
    stars = sum(repo["stargazers_count"] for repo in repos)

    print(f"{user}: {len(repos)} public repositories, {stars} stars in total")
    print()
    for repo in sorted(repos, key=lambda item: item["pushed_at"], reverse=True):
        language = repo["language"] or "-"
        print(f"{repo['name']:<32} {language:<12} {repo['stargazers_count']:>3} stars  pushed {repo['pushed_at'][:10]}")
    print()
    print("Languages:", ", ".join(f"{name} ({count})" for name, count in languages.most_common()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
