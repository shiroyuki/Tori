from distutils.core import setup

setup(
    name         = 'tori',
    version      = '2.2.0d',
    description  = 'Micro Web Framework and ORM for MongoDB',
    author       = 'Juti Noppornpitak',
    author_email = 'juti_n@yahoo.co.jp',
    url          = 'http://shiroyuki.com/work/projects-tori',
    packages     = [
        'demo',
        'demo.app',
        'demo.app.controller',
        'demo.app.views',
        'demo.resources',
        'tori',
        'tori.cli',
        'tori.data',
        'tori.db',
        'tori.db.driver',
        'tori.decorator',
        'tori.session',
        'tori.session.entity',
        'tori.session.repository',
        'tori.socket',
        'tori.template'
    ],
    scripts          = ['bin/nest'],
    install_requires = ['imagination', 'kotoba', 'tornado', 'jinja2', 'pymongo']
)
