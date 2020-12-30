#!/usr/bin/env python
import os
from setuptools import setup
import shutil


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


if not os.path.exists('build'):
    os.mkdir('build')
scripts = (
    'main.py',
    'read_bin.py',
)
scripts_dist = []
for script in scripts:
    # Make script names more executable like
    if script == "main.py":
        dst = 'build/bpwahk'
    else:
        dst_base = script
        dst_base = dst_base.replace('.py', '')
        dst_base = dst_base.replace('.sh', '')
        dst_base = dst_base.replace('_', '-')
        dst = 'build/bpwahk-' + dst_base
    if os.path.exists(dst):
        os.unlink(dst)
    os.symlink(os.path.realpath(script), dst)
    scripts_dist.append(dst)

setup(
    name="bpwahk",
    version="1.0.0",
    author="John McMaster",
    author_email='JohnDMcMaster@gmail.com',
    description=("BPWin AutoHotKey RPC binding"),
    license="BSD",
    keywords="bpmicrosystems autohotkey",
    url='https://github.com/JohnDMcMaster/bpwahk',
    packages=["bpwahk"],
    scripts=scripts_dist,
    install_requires=[],
    long_description="bpwahk go vroom",
    classifiers=[
        "License :: OSI Approved :: BSD License",
    ],
)
