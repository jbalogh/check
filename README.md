A script that runs pyflakes & pep8.py on your Python files, and a trailing
whitespace checker on all the rest.  Keeps anal-retentive style nazis like me
happy, and should (in theory) make your code look nicer.

With no arguments it looks at any added or modified files according to your
vcs's `status` command (git or svn at the moment).  With arguments, it will
check those files and recurse into directories.

Best installed with pip or easy_install so you also get the pyflakes dependency.
