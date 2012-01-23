'''
A sample application using SimpleApplication.

:author: Juti Noppornpitak <juti_n@yahoo.co.jp>
'''

import bootstrap
from   tori.application import SimpleApplication
from   app.controller   import main

application = SimpleApplication(
    {u'/': main.MainController}
)
application.listen().start()