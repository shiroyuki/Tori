'''
A sample application using DIApplication.

:author: Juti Noppornpitak <juti_n@yahoo.co.jp>
'''

import bootstrap

from tori.application   import SimpleApplication
from tori.controller    import Controller

from app.controller     import main

application = SimpleApplication(
    {u'/': main.MainController}
)
application.listen().start()
