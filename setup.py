# -*- coding: utf-8 -*-
import io
import os
import re
import sys

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    return io.open(os.path.join(here, *parts), 'r').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


setup_requirements = ['pytest-runner'] if {'pytest', 'test', 'ptr'}.intersection(sys.argv) else []
install_requirements = ['babelfish>=0.5.2', 'enzyme>=0.4.1', 'pint>=0.8', 'pymediainfo>=2.1.5', 'PyYAML',
                        'six>=1.9.0']
test_requirements = ['flake8_docstrings', 'flake8-import-order', 'pydocstyle',
                     'pep8-naming', 'pytest>=2.8', 'pytest-cov', 'pytest-flake8']

if sys.version_info < (3, 3):
    test_requirements.append('mock')

setup(
    name='knowit',
    version=find_version('knowit', '__init__.py'),
    description='Know better your media files',
    long_description=read('README.rst'),
    keywords='video mkv mp4 mediainfo metadata movie episode tv shows series',
    author='Rato AQ2',
    author_email='rato.aq2@gmail.com',
    url='https://github.com/ratoaq2/knowit',
    license='MIT',
    entry_points={
        'console_scripts': [
            'knowit = knowit.__main__:main'
        ]},
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Multimedia :: Video'
    ],
    packages=find_packages(exclude=('tests', 'docs')),
    include_package_data=True,
    setup_requires=setup_requirements,
    install_requires=install_requirements,
    tests_require=test_requirements,
    extras_require={
        'test': test_requirements,
    },
)
