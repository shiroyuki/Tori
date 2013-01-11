from distutils.core import setup

setup(
    name         = 'Tori',
    version      = '2.0',
    description  = 'Micro Web Framework',
    author       = 'Juti Noppornpitak',
    author_email = 'juti_n@yahoo.co.jp',
    url          = 'http://shiroyuki.com/work/projects-tori',
    packages     = ['tori', 'tori.data', 'tori.db', 'tori.decorator', 'tori.session', 'tori.socket', 'tori.template'],
    scripts      = ['bin/nest']
)
