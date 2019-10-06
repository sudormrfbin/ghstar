#!/usr/bin/env python3

import os
import sys
import argparse
import textwrap
import collections

import requests
import requests.exceptions


Repo = collections.namedtuple("Repo", ["full_name", "description", "stars"])


class AuthError(Exception):
    """Raised when invalid credentials are supplied."""

    def __init__(self):
        msg = (
            "Invalid credentials supplied.\n"
            "Please set the environment variables GH_UNAME and GH_TOKEN "
            "to your GitHub username and access token."
        )
        super().__init__(msg)


class InvalidRepoError(Exception):
    """Raised when a given repo is invalid."""

    def __init__(self, repo):
        msg = "{} is not a valid repo.".format(repo.full_name)
        super().__init__(msg)


def get_argparser():
    """Returns an `ArgumentParser()` for parsing command line options."""
    example_text = textwrap.dedent(  # ignore common whitespace for all lines
        """
        examples:
          ghstar gokulsoumya/ghstar
          ghstar jlevy/the-art-of-command-line
        """
    )

    parser = argparse.ArgumentParser(
        prog="ghstar",
        description="Star GitHub repos from the command line.",
        epilog=example_text,
        # specify formatter_class to preserve newlines in epilog
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("repo", help="Name of repo to star")
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Search for a repo and star interactively",
    )

    return parser


def get_credentials():
    """
    Get GitHub user credentials from the environment variables
    `GH_UNAME` and `GH_TOKEN`.

    Returns:
        tuple: Credentials as a tuple of (username, token).

    Raises:
        AuthError: If username or token is empty.
    """

    gh_user = os.getenv("GH_UNAME")
    gh_token = os.getenv("GH_TOKEN")

    if not (gh_user and gh_token):
        raise AuthError()

    return (gh_user, gh_token)


def search_repo(query, gh_user, gh_token):
    """
    Search for a repo on GitHub. Searches in the project's description
    and readme.

    Returns:
        sequence of Repo: Repositories matching the search query.
    """
    try:
        r = requests.get(
            url="https://api.github.com/search/repositories",
            auth=(gh_user, gh_token),
            params={"q": query},
        )
    except requests.exceptions.ConnectionError:
        raise ConnectionError("Please check your internet connection.")

    result = []

    for repo_item in r.json()["items"]:
        result.append(
            Repo(
                repo_item["full_name"],
                repo_item["description"],
                repo_item["stargazers_count"],
            )
        )

    return result


def select_repo(repos):
    """
    Select a repo from a list of repos, preferably returned after a search.

    Args:
        repos (sequence of Repo): Repositories to choose from.

    Returns:
        Repo: The user selected repository.
    """
    print()
    for index, repo in enumerate(repos):
        print(
            "[{number}] {repo_name} - {desc} ({stars} stars)".format(
                number=index + 1,
                repo_name=repo.full_name,
                desc=repo.description,
                stars=repo.stars,
            )
        )
    print()

    number = input("Select the repository [1-{}]: ".format(len(repos)))
    return repos[int(number) - 1]


def star_repo(repo, gh_user, gh_token):
    """
    Star a repo on GitHub.

    Args:
        repo (Repo): Repository to star.

    Raises:
        AuthError: Invalid user credentials.
        InvalidRepoError: Invalid repo name.
        ConnectionError: No internet connection.
    """
    try:
        r = requests.put(
            url="https://api.github.com/user/starred/" + repo.full_name,
            auth=(gh_user, gh_token),
            headers={"Content-Length": "0"},
        )
    except requests.exceptions.ConnectionError:
        raise ConnectionError("Please check your internet connection.")

    if r.status_code == 401:
        raise AuthError()
    elif r.status_code == 404:
        raise InvalidRepoError(repo)


def main():
    parser = get_argparser()
    args = parser.parse_args()

    try:
        username, token = get_credentials()
        if args.interactive:
            search_results = search_repo(
                query=args.repo, gh_user=username, gh_token=token
            )
            repo = select_repo(search_results)
        else:
            repo = Repo(full_name=args.repo, description=None, stars=None)

        star_repo(repo=repo, gh_user=username, gh_token=token)

    except (AuthError, InvalidRepoError, ConnectionError) as error:
        exit(error)

    print("Starred " + repo.full_name)
    exit(0)


if __name__ == "__main__":
    main()
