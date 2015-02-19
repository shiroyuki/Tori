try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(
    name         = 'tori',
    version      = '3.1.0a1',
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
        'tori.template',
        'demo',
        'demo.app',
        'demo.app.controller',
        'demo.app.views',
        'demo.resources'
    ],
    scripts          = ['bin/nest'],
    install_requires = ['passerine', 'imagination', 'kotoba', 'tornado', 'jinja2']
)
