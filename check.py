#!/usr/bin/env python
from __future__ import with_statement

import contextlib
import fnmatch
import os
import re
import subprocess
import sys
from cStringIO import StringIO

VCS = ('svn', 'git')

# Not using re.VERBOSE because we need to match a '#' for git.
RE = {'svn': "^(?:A|M)\s+" # Find Added or Modified files.
             "(.*)$",      # Store the rest of the line (the filepath).

      'git': "^#\s+"       # The line starts with an octothorpe and whitespace.
             "(?:new file|modified):\s+"  # Look for new/modified files.
             "(.*)$",      #  Store the rest of the line (the filepath).
      }


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
def checker(glob):
    """Decorator to register `func` in `checkers` and normalize output."""
    def decorator(func):
        def helper(files):
            matching_files = dict((k, v) for k, v in files.iteritems()
                                  if fnmatch.fnmatch(k, glob))
            if not matching_files:
                return
            with captured_output() as stream:
                func(matching_files)
                stream.seek(0)
                output = stream.read()
            if output.strip():
                print '*' * 5, func.__name__, '*' * (43 - len(func.__name__))
                print output
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
    if vcs in VCS:
        out = call([vcs, 'status'])
        out = out.splitlines()
        r = re.compile(RE[vcs])
        return [m[0] for m in filter(None, map(r.findall, out))]
    else:
        raise Exception("Unsupported vcs %s." % vcs)


def call(seq):
    """Use Popen to execute `seq` and return stdout."""
    proc = subprocess.Popen(seq, stdout=subprocess.PIPE)
    return proc.communicate()[0]


def pyfiles(files):
    return [f for f in files.keys() if f.endswith('.py')]


@checker('*.py')
def pyflakes(files):
    print call(['pyflakes'] + files.keys())


@checker('*.py')
def pep8(files):
    print call(['pep8.py', '--repeat'] + files.keys())


@checker('*')
def trailing_whitespace(files):
    r = re.compile('\s+$')
    for filename, content in files.iteritems():
        for idx, line in enumerate(content.splitlines()):
            if r.search(line):
                print '%s:%d: trailing whitespace' % (filename, idx + 1)


def _main():
    if len(sys.argv) == 1:
        # If there are no arguments, figure out what to do based on VCS
        vcs = which_vcs()
        files = set(interesting_files(vcs))
    else:
        # Run checks on the files specified by the command-line arguments
        in_files = sys.argv[1:]
        # Note that the order of the files checked is not preserved when
        # directories are present in argv.
        files = []
        for file in in_files:
            # Ignore dot-files
            if file.startswith("."):
                continue
            # Handle the contents of directories
            if os.path.isdir(file):
                cur_dir = file
                in_files.extend(os.path.join(cur_dir, new_file)
                                for new_file in os.listdir(cur_dir))
            else:
                files.append(file)

    d = dict((filename, open(filename).read()) for filename in files
             if os.path.isfile(filename))
    for checker in checkers:
        checker(d)

if __name__ == '__main__':
    _main()
