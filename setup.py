from distutils.core import setup

setup(
    name         = 'Tori',
    version      = '2.1',
    description  = 'Micro Web Framework',
    author       = 'Juti Noppornpitak',
    author_email = 'juti_n@yahoo.co.jp',
    url          = 'http://shiroyuki.com/work/projects-tori',
    packages     = [
        'tori',
        'tori.data',
        'tori.db',
        'tori.decorator',
        'tori.session',
        'tori.session.entity',
        'tori.session.entity.base',
        'tori.session.entity.database',
        'tori.session.entity.document',
        'tori.session.repository',
        'tori.session.repository.base',
        'tori.session.repository.collection',
        'tori.session.repository.database',
        'tori.session.repository.memory',
        'tori.session.repository.xredis',
        'tori.socket',
        'tori.template'
    ],
    scripts      = ['bin/nest'],
    install_requires = ['imagination', 'kotoba', 'tornado', 'jinja2', 'pymongo']
)
