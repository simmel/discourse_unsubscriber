#!/usr/bin/env python3
# pylint: disable=fixme,missing-docstring
from setuptools import setup

setup(
    name="discourse_unsubscriber",
    versioning="distance",  # Optional, would activate tag_based versioning
    setup_requires=["setupmeta"],  # FIXME Maybe setuptools_scm?
    extras_require={"dev": ["pylint>=2.3", "flake8>=3.7"]},
    entry_points={
        "console_scripts": ["discourse_unsubscriber=discourse_unsubscriber:main"]
    },
)
