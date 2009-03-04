from distutils.core import setup

setup(name='check',
      version='0.3',
      scripts=['check.py', 'pep8.py'],
      install_requires=['pyflakes'],
)
