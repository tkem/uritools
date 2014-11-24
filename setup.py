import os.path, codecs, re

from setuptools import setup


with codecs.open(os.path.join(os.path.dirname(__file__), 'uritools', '__init__.py'),
                 encoding='utf8') as f:
    metadata = dict(re.findall(r"__([a-z]+)__ = '([^']+)", f.read()))


setup(
    name='uritools',
    version=metadata['version'],
    author='Thomas Kemmer',
    author_email='tkemmer@computer.org',
    url='https://github.com/tkem/uritools/',
    license='MIT',
    description='RFC 3986 compliant, Unicode-aware, scheme-agnostic replacement for urlparse',
    long_description=open('README.rst').read(),
    keywords='uri url urlparse urlsplit urljoin urldefrag',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    packages=['uritools'],
    test_suite='tests'
)
