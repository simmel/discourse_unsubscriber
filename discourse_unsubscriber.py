#!/usr/bin/env python3
# pylint: disable=ungrouped-imports
"""
    license: ISC
    author: Simon Lundström simmel@soy.se
"""

import argparse
import email
import logging
import os
import signal
import sys
from email.header import decode_header
from email.message import EmailMessage
from pathlib import Path

import mechanize
import persistqueue
import persistqueue.serializers.json
import xdg
from tenacity import after_log, retry, wait_fixed

__version__ = "0.0.0"

__url__ = "https://github.com/simmel/discourse_unsubscriber"

__app__ = Path(sys.argv[0]).stem


def client(
    *,  # pylint: disable=bad-continuation
    work: persistqueue.UniqueQ,
    status: persistqueue.SQLiteQueue,
    log: logging.Logger,
    args: argparse.Namespace,
) -> None:
    "Parse mail, extract URL and submit to queue"

    # Parse email and extract URL in List-Unsubscribe header
    mail = email.message_from_file(sys.stdin, EmailMessage)
    # Decode any RFC2047 encoding
    # I feel like this type error is out of my hands
    decoded_header = decode_header(mail["List-Unsubscribe"])  # type: ignore
    # Make it a header again to get UTF-8 or latin1 encoding for free
    # Also, force it to string and strip any whitespace
    header_as_str = str(email.header.make_header(decoded_header)).strip()
    # Remove any quoting like brackets
    unsubscribe_url = email.utils.unquote(header_as_str)

    def print_status(args: argparse.Namespace, status: persistqueue.SQLiteQueue):
        if args.debug:
            log.debug("{}: {}".format(os.getpid(), status.get()))
        else:
            print("\033[H{}: {}".format(os.getpid(), status.get()))

    def enqueue_work(work: persistqueue.UniqueQ, unsubscribe_url: str):
        work.put(unsubscribe_url)

    if args.debug is not None and not args.debug:
        newpid = os.fork()
        if newpid == 0:
            print_status(args, status)
        else:
            enqueue_work(work, unsubscribe_url)
    else:
        enqueue_work(work, unsubscribe_url)
        print_status(args, status)


def server(
    *,  # pylint: disable=bad-continuation
    work: persistqueue.UniqueQ,
    status: persistqueue.SQLiteQueue,
    log: logging.Logger,
    args: argparse.Namespace,
) -> None:
    "Read URL from queue, send to Discourse and retry for any HTTP errors"

    log.info("Server running")
    browser = mechanize.Browser()
    # Discourse doesn't let robots visit /email but we're not a real robot,
    # right?
    # pylint: disable=no-member
    browser.set_handle_robots(False)
    if args.debug:
        browser.set_debug_http(True)
        browser.set_debug_redirects(True)
        browser.set_debug_responses(True)
    browser.set_header(
        "User-Agent",
        # Admit our affiliation with Mechanize
        "{name}/{version} (+{url}) WWW-Mechanize/{py_version}".format(
            name=__app__, version=__version__, url=__url__, py_version=sys.version[:3]
        ),
    )

    @retry(wait=wait_fixed(10), after=after_log(log, logging.INFO))
    def unsubscribe(
        work: persistqueue.UniqueQ,
        status: persistqueue.SQLiteQueue,
        log: logging.Logger,
    ) -> None:
        url = work.get()
        log.debug(url)

        # pylint: disable=no-member,assignment-from-none
        response = browser.open(url)
        log.debug("{code} {url}".format(code=response.getcode(), url=response.geturl()))
        browser.select_form(nr=0)
        response = browser.submit()
        log.debug("{code} {url}".format(code=response.getcode(), url=response.geturl()))
        work.task_done()
        status.put("{} done".format(url))

    while True:
        unsubscribe(work, status, log)


def main():
    "main"

    log = logging.getLogger()
    log.addHandler(logging.StreamHandler(sys.stdout))
    log.setLevel(logging.INFO)

    # Avoid that pesky KeyboardInterrupt
    def sigint(_signal, _frame):
        sys.exit(0)

    signal.signal(signal.SIGINT, sigint)
    parser = argparse.ArgumentParser(
        description="Unsubscribe from Discourse threads easily"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debugging")

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

    # Set log level
    if args.debug:
        log.setLevel(logging.DEBUG)

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
    args.variant(work=work, status=status, log=log, args=args)


if __name__ == "__main__":
    main()
