#from os.path import basename, dirname, join
#from glob    import glob

from imagination.locator import Locator
#from tori.service import ServiceLocator

__version__ = '2.0a'

settings = {}
services = Locator()

# __all__     = []
# 
# for __submodule_name in glob(join(dirname(__file__), '*.py')):
#     __submodule_name = basename(__submodule_name[:-3])
#     
#     if __submodule_name == '__init__':  continue
#     
#     # Automatically import the submodule.
#     __import__('tori.%s' % __submodule_name)
#     
#     # Declare the auto-loaded submodule.
#     __all__.append(__submodule_name)