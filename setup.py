try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(
    name         = 'tori',
    version      = '3.1.2',
    description  = 'A collection of libraries and a micro web framework based on Tornado framework',
    license      = 'MIT',
    author       = 'Juti Noppornpitak',
    author_email = 'juti_n@yahoo.co.jp',
    url          = 'http://shiroyuki.com/projects/tori.html',
    packages     = [
        'tori',
        'tori.cli',
        'tori.data',
        'tori.decorator',
        'tori.session',
        'tori.session.entity',
        'tori.session.repository',
        'tori.socket',
        'tori.template'
    ],
    classifiers   = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries'
    ],
    scripts          = ['bin/nest'],
    install_requires = ['passerine', 'imagination', 'kotoba', 'tornado', 'jinja2']
)
