import unittest
import bootstrap

from tori.common import console

console.disable_logging()

##### DEBUGGING CODE: BEGIN #####
import sys, os
modules = sys.modules.keys()
modules.sort()
#print ', '.join(modules)
for k, v in sys.modules.iteritems():
    if 'tori' not in k or not v: continue
    print k, v
    print dir(v)
    print os.path.dirname(v.__file__)
    #break
##### DEBUGGING CODE: END #######

suite = unittest.TestLoader().discover(
    bootstrap.testing_base_path,
    pattern='test_*.py'
)
unittest.TextTestRunner(verbosity=1).run(suite)