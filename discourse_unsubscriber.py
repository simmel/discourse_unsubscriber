#!/usr/bin/env python3
# pylint: disable=
"""
license: ISC
author: Simon Lundström simmel@soy.se
"""

import argparse

__version__ = "0.0.0"

__url__ = "https://github.com/simmel/discourse_unsubscriber"


def client():
    "Parse mail, extract URL and submit to queue"


def server():
    "Read URL from queue, send to Discourse and retry for any HTTP errors"


def main():
    "main"
    parser = argparse.ArgumentParser(
        description="Unsubscribe from Discourse threads easily"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--client",
        dest="variant",
        action="store_const",
        const=client,
        help="Start as a client e.g. from mutt",
    )
    group.add_argument(
        "--server",
        dest="variant",
        action="store_const",
        const=server,
        help="Start as a server",
    )
    args = parser.parse_args()

    print(args.variant)


if __name__ == "__main__":
    main()
