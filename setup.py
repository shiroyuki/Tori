try:
    from setuptools import setup
except:
    from distutils.core import setup

if sys.version_info < _minimum_version:
    raise RuntimeError('Required Python {}'.format(
        '.'.join([str(i) for i in _minimum_version])
    ))

setup(
    name         = 'tori',
    version      = '4.0.0a1',
    description  = 'A micro web framework based on Tornado and Flask framework',
    license      = 'MIT',
    author       = 'Juti Noppornpitak',
    author_email = 'juti_n@yahoo.co.jp',
    url          = 'http://shiroyuki.com/projects/tori.html',
    packages     = [
        'tori',
        'tori.cli',
    ],
    classifiers   = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries'
    ],
    scripts          = ['bin/tori'],
    install_requires = ['flask', 'imagination', 'kotoba', 'tornado', 'jinja2', 'pyyaml']
)
