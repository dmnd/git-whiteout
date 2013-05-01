#!/usr/bin/env python

import fileinput
import os.path
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


sha = git("rev-parse", "--verify",  "HEAD").strip()
files = get_files(sha)

print "Old commit was {}".format(sha)

print "Rewinding back to HEAD^1..."
git("reset", "HEAD^1")

print "Backing up changed files..."
tmpdir = tempfile.mkdtemp()
for f in files:
    shutil.move(f, os.path.join(tmpdir, f))
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
