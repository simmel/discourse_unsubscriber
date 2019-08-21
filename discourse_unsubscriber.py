#!/usr/bin/env python3
# pylint: disable=
"""
    license: ISC
    author: Simon Lundström simmel@soy.se
"""

import argparse
import email
import os
import signal
import sys
from email.header import decode_header
from email.message import EmailMessage
from pathlib import Path

import persistqueue
import persistqueue.serializers.json
import xdg

__version__ = "0.0.0"

__url__ = "https://github.com/simmel/discourse_unsubscriber"


def client(work=None, status=None):
    "Parse mail, extract URL and submit to queue"

    # Parse email and extract URL in List-Unsubscribe header
    mail = email.message_from_file(sys.stdin, EmailMessage)
    # Decode any RFC2047 encoding
    decoded_header = decode_header(mail["List-Unsubscribe"])
    # Make it a header again to get UTF-8 or latin1 encoding for free
    # Also, force it to string and strip any whitespace
    header_as_str = str(email.header.make_header(decoded_header)).strip()
    # Remove any quoting like brackets
    unsubscribe_url = email.utils.unquote(header_as_str)

    newpid = os.fork()
    if newpid == 0:
        print("\033[H{}: {}".format(os.getpid(), status.get()))
    else:
        print("parent: {} child: {}".format(os.getpid(), newpid))
        work.put(unsubscribe_url)


def server(work=None, status=None):
    "Read URL from queue, send to Discourse and retry for any HTTP errors"

    while True:
        url = work.get()
        print(url)
        work.task_done()
        status.put("{} done".format(url))


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
    queue_path = Path(xdg.XDG_CACHE_HOME) / Path(sys.argv[0]).stem
    # Setup the work queue where we submit the work
    work = persistqueue.UniqueQ(
        queue_path,
        name="work",
        auto_commit=False,
        # We're running from multiple processes so we're "multithreaded"
        multithreading=True,
        # Might be more readable if we need to do some disaster recovery?
        # ¯\_(ツ)_/¯
        serializer=persistqueue.serializers.json,
    )
    # Setup the status queue where the server will submit the status of the API
    # call
    status = persistqueue.SQLiteQueue(
        queue_path,
        name="status",
        # Even though this is the default it won't auto ack until we set it to
        # true.
        auto_commit=True,
        # We're running from multiple processes so we're "multithreaded"
        multithreading=True,
        # Might be more readable if we need to do some disaster recovery?
        # ¯\_(ツ)_/¯
        serializer=persistqueue.serializers.json,
    )
    args.variant(work, status)


if __name__ == "__main__":
    main()
