"""
A sample application using Application.

:author: Juti Noppornpitak <juti_n@yahoo.co.jp>
"""

from time import time

import bootstrap

from   tori.application import Application

time_at_blank_state = time()
application = Application('server.xml')
time_at_prepared_state = time()
print('Time elapsed on setup: {}'.format(time_at_prepared_state - time_at_blank_state))
application.start()
