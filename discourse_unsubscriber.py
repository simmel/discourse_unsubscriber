#!/usr/bin/env python3
# pylint: disable=
"""
license: ISC
author: Simon Lundström simmel@soy.se
"""

import argparse

__version__ = "0.0.0"

__url__ = "https://github.com/simmel/discourse_unsubscriber"


def main():
    "main"
    parser = argparse.ArgumentParser(
        description="Unsubscribe from Discourse threads easily"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--client", action="store_true", help="Start as a client e.g. from mutt"
    )
    group.add_argument("--server", action="store_true", help="Start as a server")
    args = parser.parse_args()

    print(__name__)


if __name__ == "__main__":
    main()
