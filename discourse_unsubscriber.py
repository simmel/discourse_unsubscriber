#!/usr/bin/env python3
# pylint: disable=
"""
    license: ISC
    author: Simon Lundström simmel@soy.se
"""

import argparse
import signal
import sys
from pathlib import Path

import persistqueue
import persistqueue.serializers.json
import xdg

__version__ = "0.0.0"

__url__ = "https://github.com/simmel/discourse_unsubscriber"


def client(queue=None):
    "Parse mail, extract URL and submit to queue"
    queue.put("\n".join(sys.stdin.readlines()).strip())


def server(queue=None):
    "Read URL from queue, send to Discourse and retry for any HTTP errors"

    while True:
        url = queue.get()
        print(url)
        queue.task_done()


def main():
    "main"

    # Avoid that pesky KeyboardInterrupt
    def sigint(_signal, _frame):
        sys.exit(0)

    signal.signal(signal.SIGINT, sigint)
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

    # Setup queue in the cache dir, should be persistent enough. At least
    # better than TMP
    queue_file = Path(xdg.XDG_CACHE_HOME) / Path(sys.argv[0]).stem
    queue = persistqueue.UniqueQ(
        queue_file,
        auto_commit=False,
        # We're running from multiple processes so we're "multithreaded"
        multithreading=True,
        # Might be more readable if we need to do some disaster recovery?
        # ¯\_(ツ)_/¯
        serializer=persistqueue.serializers.json,
    )
    args.variant(queue)


if __name__ == "__main__":
    main()
