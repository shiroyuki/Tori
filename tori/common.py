'''
:Author: Juti Noppornpitak

This package contains classes and functions for common use.
'''
import os
import re
import sys
import time

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
    def warn(message):
        Console.__print('WARN', message)
    