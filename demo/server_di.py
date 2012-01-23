'''
A sample application using DIApplication.

:author: Juti Noppornpitak <juti_n@yahoo.co.jp>
'''

import bootstrap

from tori.application   import DIApplication
from tori.controller    import Controller

application = DIApplication('server.xml')
application.start()
