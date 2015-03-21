#!/usr/bin/env python
from setuptools import setup, find_packages
from txque import version

setup(
    name="txque",
    version=version,
    description="txque is a Python library for running asynchronous jobs using Twisted.",
    author="Brian Muller",
    author_email="bamuller@gmail.com",
    license="MIT",
    url="http://github.com/bmuller/txque",
    packages=find_packages(),
    requires=["twisted", "twistar"],
    install_requires=['twisted>=14.0', "twistar>=1.3"]
)
