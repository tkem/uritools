import sys

from setuptools import find_packages, setup

# environment markers require a recent setuptools and/or pip version
if sys.version_info >= (3, 3) or 'bdist_wheel' in sys.argv:
    install_requires = []
else:
    install_requires = ['ipaddress']


def get_version(filename):
    from re import findall
    with open(filename) as f:
        metadata = dict(findall("__([a-z]+)__ = '([^']+)'", f.read()))
    return metadata['version']

setup(
    name='uritools',
    version=get_version('uritools/__init__.py'),
    url='https://github.com/tkem/uritools/',
    license='MIT',
    author='Thomas Kemmer',
    author_email='tkemmer@computer.org',
    description=(
        'RFC 3986 compliant, Unicode-aware, scheme-agnostic '
        'replacement for urlparse'
    ),
    long_description=open('README.rst').read(),
    keywords='uri url urlparse urlsplit urljoin urldefrag',
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=install_requires,
    extras_require={
        ':python_version == "2.7"': ['ipaddress']
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Other Environment',
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
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
