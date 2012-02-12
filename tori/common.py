import re
import sys

def get_class_reference(controller_path):
    access_path     = re.split('\.', controller_path)
    module_name     = '.'.join(access_path[:-1])
    controller_name = access_path[-1]
    
    __import__(module_name, fromlist=[controller_name])
    return getattr(sys.modules[module_name], controller_name)

class console(object):
    _log_disabled = False
    
    @staticmethod
    def disable_logging():
        console._log_disabled = True
    
    @staticmethod
    def log(msg):
        if console._log_disabled:
            return
        
        print msg
    
    @staticmethod
    def warn(msg):
        print msg
    