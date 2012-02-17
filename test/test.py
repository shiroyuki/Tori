import unittest
import bootstrap

from tori.common import console

console.disable_logging()

##### DEBUGGING CODE: BEGIN #####
#import sys
#modules = sys.modules.keys()
#modules.sort()
#print '\n'.join(modules)
##### DEBUGGING CODE: END #######

suite = unittest.TestLoader().discover(
    bootstrap.testing_base_path,
    pattern='test_*.py'
)
unittest.TextTestRunner(verbosity=1).run(suite)