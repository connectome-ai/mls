# pylint: skip-file

import distutils.cmd
import distutils.log
import os
import subprocess

from setuptools import find_packages, setup


class PylintCommand(distutils.cmd.Command):
    """A custom command to run Pylint on all Python source files."""

    description = 'run Pylint on Python source files'
    user_options = [
        # The format is (long option, short option, description).
        ('pylint-rcfile=', None, 'path to Pylint config file'),
    ]

    def initialize_options(self):
        """Set default values for options."""
        # Each user option must be listed here with their default value.
        self.pylint_rcfile = '.pylintrc'

    def finalize_options(self):
        """Post-process options."""
        if self.pylint_rcfile:
            assert os.path.exists(self.pylint_rcfile), (
                'Pylint config file %s does not exist.' % self.pylint_rcfile)

    def run(self):
        """Run command."""
        command = ['pylint']
        if self.pylint_rcfile:
            command.append('--rcfile=%s' % self.pylint_rcfile)
        command.append(os.getcwd() + '/mls')
        self.announce(
            'Running command: %s' % str(command),
            level=distutils.log.INFO)
        subprocess.check_call(command)


tests_require = [
    'numpy>=1.12.1',
]

install_requires = [
    'requests>=2.13.0',
    'Werkzeug>=0.12.1'
]

CONFIG = {
    'name': 'myLittleServer',
    'url': 'https://github.com/connectome-ai/mls',
    'download_url': 'https://github.com/connectome-ai/mls/archive/1.2.3.tar.gz',
    'version': '1.2.3',
    'description': 'mls is a wrapper around ml code.',
    'author': 'connectome.ai',
    'test_suite': 'mls',
    'packages': find_packages(exclude=['tests', '*.tests', '*.tests.*']),
    'tests_require': tests_require,
    'install_requires': install_requires,
    'cmdclass': {
        'pylint': PylintCommand
    },
}

setup(**CONFIG)
