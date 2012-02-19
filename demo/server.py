'''
A sample application using DIApplication.

:author: Juti Noppornpitak <juti_n@yahoo.co.jp>
'''

import bootstrap
from   tori.application import DIApplication

application = DIApplication('server.xml')

if False:
    import sys, os
    modules = sys.modules.keys()
    modules.sort()
    #print ', '.join(modules)
    for k, v in sys.modules.iteritems():
        if 'tori' not in k or not v: continue
        print k, v
        print dir(v)
        print os.path.dirname(v.__file__)

application.start()
