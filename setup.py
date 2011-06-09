from distutils.core import setup

setup(name='check',
      version='0.4pre',
      scripts=['check.py'],
      install_requires=['pyflakes', 'pep8', 'path.py'],
)
