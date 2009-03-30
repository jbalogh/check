from __future__ import with_statement

import sys

from nose.tools import assert_raises
from mock import patch

import check


@patch('check.StringIO')
def test_captured_output(stream_mock):
    """stdout should be a StringIO in the with statement."""
    # Can't assert that stdout is a file because nose may be capturing stdout.
    mock = stream_mock()
    with check.captured_output() as stream:
        assert stream is mock
        assert sys.stdout is mock


@patch('check.os')
def test_which_vcs_fail(os_mock):
    os_mock.path.exists.return_value = False
    assert_raises(Exception, check.which_vcs)


@patch('check.os')
def test_which_vcs_success(os_mock):
    os_mock.path.exists.return_value = False
    # Make sure getcwd is always different.
    os_mock.getcwd = range(20).pop

    # A chdir that flips os.path.exists after being called 3 times.
    calls = [0]
    def mock_chdir(path):
        calls[0] += 1
        if calls[0] == 3:
            os_mock.path.exists.return_value = True

    os_mock.chdir = mock_chdir

    vcs = check.which_vcs()
    # We iterate over VCS looking for matches, so which_vcs will return
    # the first key when it succeeds.
    assert vcs == check.VCS.keys()[0]
    assert os_mock.path.exists.call_count == 1 + 3 * len(check.VCS)


@patch('check.call')
def test_interesting_files(call_mock):
    expected = ['foo', 'bar']
    call_mock.return_value = git_status
    assert check.interesting_files('git') == expected

    call_mock.return_value = svn_status
    assert check.interesting_files('svn') == expected

git_status = """
# On branch master
# Changed but not updated:
#   (use "git add <file>..." to update what will be committed)
#   (use "git checkout -- <file>..." to discard changes in working directory)
#       new file:   foo
#
#       modified:   bar
"""

svn_status = """
A      foo
?      wtf
M      bar
"""


@patch('check.call')
def test_pyflakes(call_mock):
    check.pyflakes(['foo', 'bar', 'bla.py', 'baz.exe'])
    call_mock.assert_called_with(['pyflakes', 'bla.py'])


@patch('check.call')
def test_pep8(call_mock):
    check.pep8(['foo', 'bar', 'bla.py', 'baz.exe'])
    call_mock.assert_called_with(['pep8.py', '--repeat', 'bla.py'])


@patch('__builtin__.open')
def test_trailing_whitespace(open_mock):
    m = open_mock.return_value.read.return_value = 'foo\nbar \n \n'
    files = ['foo', 'bla.py']
    with check.captured_output() as output:
        check.trailing_whitespace(files)
    output.reset()
    # Ignore the banner.
    output.readline()

    for n in 2, 3:
        assert output.readline() == '%s:%s: trailing whitespace\n' % ('foo', n)
