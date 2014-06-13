#!/usr/bin/env python
from __future__ import with_statement

import os
import re
import sys
import fnmatch
import functools
import contextlib
import subprocess
from cStringIO import StringIO

from path import path

# Not using re.VERBOSE because we need to match a '#' for git.
VCS = {'svn': "^(?:A|M)\s+" # Find Added or Modified files.
              "(.*)$",      # Store the rest of the line (the filepath).

       'git': "^#?\s+"     # The line starts with an octothorpe and whitespace.
              "(?:new file|modified):\s+"  # Look for new/modified files.
              "(.*)$",    #  Store the rest of the line (the filepath).
       }


IGNORE = ['.*', '*~', '*.py[co]', '*.egg', '*.sqlite']


@contextlib.contextmanager
def captured_output():
    """Temporarily redirects stdout to the yielded stream."""
    stdout = sys.stdout
    stream = StringIO()
    sys.stdout = stream
    try:
        yield stream
    finally:
        sys.stdout = stdout


checkers = []
def checker(include='*', excludes=[]):
    """Decorator to register `func` in `checkers` and normalize output."""
    def decorator(func):
        @functools.wraps(func)
        def helper(files):
            files = fnmatch.filter(files, include)
            for expattern in excludes:
                files = [f for f in files
                         if not fnmatch.fnmatch(f, expattern)]
            if not files:
                return ""
            return func(files).strip()
        checkers.append(helper)
        return helper
    return decorator


def which_vcs():
    """Determine the vcs to use by looking for a '.<vcs>' directory."""
    while 1:
        for vcs in VCS:
            if os.path.exists('.%s' % vcs):
                return vcs
        prev = os.getcwd()
        os.chdir('..')
        if prev == os.getcwd():
            # At the filesystem root, so give up.
            raise Exception("No version control system found.")


def interesting_files(vcs):
    """Return a list of added or modified files."""
    out = call([vcs, 'status']).splitlines()
    r = re.compile(VCS[vcs])
    return [m[0] for m in filter(None, map(r.findall, out))]


def call(seq):
    """Use Popen to execute `seq` and return stdout."""
    return subprocess.Popen(seq,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT).communicate()[0]


@checker('*.py')
def pyflakes(files):
    return call(['pyflakes'] + files)


@checker('*.py')
def pep8(files):
    return call(['pep8', '--repeat'] + files)


@checker(excludes=['*.py', '*.json'])
def trailing_whitespace(files):
    output = []
    r = re.compile('\s+$')
    for filename in files:
        content = open(filename).read()
        for idx, line in enumerate(content.splitlines()):
            if r.search(line):
                output.append('%s:%d: trailing whitespace' % (filename, idx + 1))
    return '\n'.join(output)


@checker('*.js')
def jshint(files):
    try:
        return call(['jshint'] + files)
    except OSError:
        print 'jshint not installed for js checking'
        return ''


def _main():
    if len(sys.argv) == 1:
        # If there are no arguments, figure out what to do based on VCS
        vcs = which_vcs()
        files = interesting_files(vcs)
    else:
        files = []
        for p in map(path, sys.argv[1:]):
            if p.isfile():
                files.append(p)
            else:
                for f in p.walkfiles():
                    if not any(fnmatch.fnmatch(f, glob) for glob in IGNORE):
                        files.append(f)

    files = filter(os.path.isfile, set(files))
    exitcode = 0
    for checker in checkers:
        ret = checker(files)
        if ret:
            print ret
            exitcode = 1

    return exitcode

if __name__ == '__main__':
    sys.exit(_main())
