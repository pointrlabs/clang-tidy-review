#!/usr/bin/env python3

# clang-tidy review
# Copyright (c) 2020 Peter Hill
# SPDX-License-Identifier: MIT
# See LICENSE for more information

import argparse
import json
import os
import pathlib
import re
import subprocess

from review import (
    PullRequest,
    message_group,
    strip_enclosing_quotes,
    create_review,
    save_metadata,
    post_review,
)


def main(
    repo,
    pr_number,
    token,
    fixes_file,
    include,
    exclude,
    max_comments,
    lgtm_comment_body,
    dry_run: bool = False
):

    pull_request = PullRequest(repo, pr_number, token)

    review = create_review(
        pull_request,
        fixes_file,
        include,
        exclude
    )

    with message_group("Saving metadata"):
        save_metadata(pr_number)

    post_review(pull_request, review, max_comments, lgtm_comment_body, dry_run)


def fix_absolute_paths(fixes_file, base_dir):
    """Update absolute paths in fixes file to new location, if
    fixes file was created outside the Actions container
    """

    basedir = pathlib.Path(base_dir).resolve()
    newbasedir = pathlib.Path(".").resolve()

    if basedir == newbasedir:
        return

    print(f"Found '{fixes_file}', updating absolute paths")
    # We might need to change some absolute paths if we're inside
    # a docker container
    with open(fixes_file, "r") as f:
        fixes = f.read()

    print(f"Replacing '{basedir}' with '{newbasedir}'", flush=True)

    modified_fixes = fixes.replace(
        str(basedir), str(newbasedir)
    )

    with open(fixes_file, "w") as f:
        f.write(modified_fixes)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a review from clang-tidy warnings"
    )
    parser.add_argument("--repo", help="Repo name in form 'owner/repo'")
    parser.add_argument("--pr", help="PR number", type=int)
    parser.add_argument("--token", help="GitHub authentication token")
    parser.add_argument(
        "--base_dir",
        help="Absolute path to initial working directory to fix absolute paths in clang-tidy fixes file",
        default=".",
    )
    parser.add_argument(
        "--fixes_file",
        help="Path to pre-generated clang-tidy fixes file",
        default="",
    )
    parser.add_argument(
        "--include",
        help="Comma-separated list of files or patterns to include",
        type=str,
        nargs="?",
        default="*.[ch],*.[ch]xx,*.[ch]pp,*.[ch]++,*.cc,*.hh",
    )
    parser.add_argument(
        "--exclude",
        help="Comma-separated list of files or patterns to exclude",
        nargs="?",
        default="",
    )
    parser.add_argument(
        "--max-comments",
        help="Maximum number of comments to post at once",
        type=int,
        default=25,
    )
    parser.add_argument(
        "--lgtm-comment-body",
        help="Message to post on PR if no issues are found. An empty string will post no LGTM comment.",
        type=str,
        default='`clang-tidy` found no issues, all clean :+1:',
    )
    parser.add_argument(
        "--dry-run", help="Run and generate review, but don't post", action="store_true"
    )

    args = parser.parse_args()

    # Remove any enclosing quotes and extra whitespace
    exclude = strip_enclosing_quotes(args.exclude).split(",")
    include = strip_enclosing_quotes(args.include).split(",")

    fixes_file = args.fixes_file
    if os.path.exists(fixes_file):
        fix_absolute_paths(fixes_file, args.base_dir)

    main(
        repo=args.repo,
        pr_number=args.pr,
        token=args.token,
        fixes_file=fixes_file,
        include=include,
        exclude=exclude,
        max_comments=args.max_comments,
        lgtm_comment_body=strip_enclosing_quotes(args.lgtm_comment_body),
        dry_run=args.dry_run
    )
