Runs `pyflakes`, `pep8.py` on your Python files. Runs `jshint` on your
Javascript and a trailing whitespace checker on all the rest.  Keeps
anal-retentive style nazis like me happy, and should (in theory) make
your code look nicer.

#### How to use it

    check.py

This will run checks on any added or modified files according to your vcs's
`status` command (git or svn at the moment).

    check.py models.py tests/

This will run checks on `models.py` and any files found recursively in the
`tests/` directory.

#### Installation

Best installed with pip or easy_install so you also get the pyflakes dependency.

The easiest way to get jshint installed is via npm:

    npm install -g jshint
