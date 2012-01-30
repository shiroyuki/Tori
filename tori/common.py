import re
import sys

def get_class_reference(controller_path):
    access_path     = re.split('\.', controller_path)
    module_name     = '.'.join(access_path[:-1])
    controller_name = access_path[-1]
    
    __import__(module_name, fromlist=[controller_name])
    return getattr(sys.modules[module_name], controller_name)