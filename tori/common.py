'''
:Author: Juti Noppornpitak

This package contains classes and functions for common use.
'''
import os
import re
import sys
import time

def get_class_reference(controller_path):
    '''
    Get a class reference.
    
    This is a shortcut for calling :meth:`Loader.package`.
    '''
    return Loader(controller_path).package()

class Finder(object):
    ''' File System API Wrapper '''
    
    def read(self, file_path, is_binary=False):
        '''
        Read a file from *file_path*.
        
        By default, read a file normally. If *is_binary* is ``True``, the method will read in binary mode.
        '''
        with open(file_path, is_binary and 'rb' or 'r') as fp:
            file_content = fp.read()
        
        fp.close()
        
        return file_content

class Loader(object):
    '''
    Loader for a Python package
    
    *path_to_package* is a string representing the package path.
    
    For example::
    
        # In this case, we load the default renderer of Tori framework.
        loader = Loader('tori.renderer.DefaultRenderer')
        # Then, instantiate the default renderer.
        renderer = loader.package()('app.views')
    
    '''
    def __init__(self, path_to_package):
        self.__path         = path_to_package
        self.__access_path  = re.split('\.', self.__path)
        self.__module_path  = '.'.join(self.__access_path[:-1])
        self.__module       = None
        self.__package_name = self.__access_path[-1]
        self.__package      = None
    
    def name(self):
        ''' Get the name of the package. '''
        return self.module().__package__
    
    def module(self):
        ''' Get a reference to the module. '''
        return self.__module or self.__retrieve_module()
    
    def package(self):
        ''' Get a reference to the package. '''
        return self.__package or self.__retrieve_package()
    
    def filename(self):
        ''' Get the path to the package. '''
        return self.module().__file__
    
    def __retrieve_module(self):
        ''' Retrieve a module by the module path. '''
        
        try:
            if self.__module_path not in sys.modules:
                __import__(self.__module_path)
            
            self.__module = sys.modules[self.__module_path]
            
            return self.__module
        except KeyError:
            return None
    
    def __retrieve_package(self):
        ''' Retrieve a package by the module path and the package name. '''
        
        __import__(self.__module_path, fromlist=[self.__package_name])
        
        return getattr(self.module(), self.__package_name)


class Console(object):
    _log_disabled   = False
    _show_timestamp = True
    
    @staticmethod
    def disable_logging():
        ''' Disable logging. '''
        Console._log_disabled = True
    
    @staticmethod
    def __print(prefix, message):
        current_timestamp = time.strftime('%Y.%m.%d %H:%M:%S %Z')
        
        prefix = '[%s / %4s]' % (current_timestamp, prefix)
        
        if message and message[0] == '\r':
            prefix  = '\r%s' % prefix
            message = message[1:]
        
        output = '%4s: %s' % (prefix, message)
        
        print output
    
    @staticmethod
    def log(message):
        ''' Log the given *message* '''
        if Console._log_disabled: return
        
        Console.__print('LOG', message)
    
    @staticmethod
    def warn(msg):
        Console.__print('WARN', message)
    