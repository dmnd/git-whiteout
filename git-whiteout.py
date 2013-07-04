#!/usr/bin/env python

import errno
import fileinput
import os
import tempfile
import shutil
import subprocess

verbose = False

def git(*args):
    cmd = ("git",) + args
    if verbose:
        print " ".join(cmd)
    return subprocess.check_output(cmd)

def get_files(sha):
    return git("diff-tree", "--no-commit-id", "--name-only", "-r", sha).split()


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise


sha = git("rev-parse", "--verify",  "HEAD").strip()
files = get_files(sha)

print "Old commit was {}".format(sha)

print "Rewinding back to HEAD^1..."
git("reset", "HEAD^1")

print "Backing up changed files..."
tmpdir = tempfile.mkdtemp()
for f in files:
    path = os.path.join(tmpdir, f)
    mkdir_p(os.path.dirname(path))
    shutil.move(f, path)
    git("checkout", "--", f)

print "Committing whitespace changes..."
for line in fileinput.input(files, inplace=1):
    print line.rstrip()
git("add", *files)
git("commit", "-m strip whitespace")

print "Committing clean changes..."
for f in files:
    shutil.move(os.path.join(tmpdir, f), f)
git("add", *files)
git("commit", "--reuse-message="+sha)

shutil.rmtree(tmpdir)
print "Done!"
