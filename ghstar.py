#!/usr/bin/env python3

import os
import argparse
import textwrap

import requests
import requests.exceptions


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


example_text = textwrap.dedent(  # ignore common whitespace for all lines
    """
    examples:
      ghstar microsoft/vscode
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
args = parser.parse_args()

gh_user = os.getenv("GH_UNAME")
gh_token = os.getenv("GH_TOKEN")

if not (gh_user and gh_token):
    exit(AuthError())

try:
    r = requests.put(
        url="https://api.github.com/user/starred/" + args.repo,
        auth=(gh_user, gh_token),
        headers={"Content-Length": "0"},
    )
except requests.exceptions.ConnectionError:
    exit(ConnectionError("Please check your internet connection."))

if r.status_code == 204:
    print("Starred " + args.repo)
    exit(0)
elif r.status_code == 401:
    exit(AuthError())
elif r.status_code == 404:
    exit(InvalidRepoError(args.repo))
