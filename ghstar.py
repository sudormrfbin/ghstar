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
        msg = "{} is not a valid repo.".format(repo)
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


def star_repo(repo, gh_user, gh_token):
    """
    Star a repo on GitHub.

    Raises:
        AuthError: Invalid user credentials.
        InvalidRepoError: Invalid repo name.
        ConnectionError: No internet connection.
    """
    try:
        r = requests.put(
            url="https://api.github.com/user/starred/" + repo,
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
        star_repo(repo=args.repo, gh_user=username, gh_token=token)
    except (AuthError, InvalidRepoError, ConnectionError) as error:
        exit(error)

    print("Starred " + args.repo)
    exit(0)


if __name__ == "__main__":
    main()
