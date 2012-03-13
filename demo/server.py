'''
A sample application using DIApplication.

:author: Juti Noppornpitak <juti_n@yahoo.co.jp>
'''

from time import time

import bootstrap

from   tori.application import DIApplication

time_at_blank_state = time()
application = DIApplication('server.xml')
time_at_prepared_state = time()
print 'Time elapsed on setup: %s' % (time_at_prepared_state - time_at_blank_state)
application.start()
