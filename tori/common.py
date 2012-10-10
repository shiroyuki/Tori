# -*- coding: utf-8 -*-

'''
:Author: Juti Noppornpitak

This package contains classes and functions for common use.
'''
import os
import hashlib
import logging
import random
import re
import sys
import time

from .decorator.common import singleton

default_logging_level = logging.DEBUG

def get_default_logging_level():
    return default_logging_level

def get_logger(name, level=None, show_time=True):
    level = get_default_logging_level()

    logging_handler = logging.StreamHandler()
    logging_handler.setLevel(level)
    logging_handler.setFormatter(
        logging.Formatter(
            '%(levelname)s %(asctime)s %(name)s: %(message)s'
            if show_time
            else '%(levelname)s %(name)s: %(message)s',
            datefmt='%Y.%m.%d %H:%M:%S %Z'
        )
    )

    logger = logging.getLogger(name)
    logger.addHandler(logging_handler)
    logger.setLevel(level)

    return logger

@singleton
class Enigma(object):
    ''' Hashlib wrapper '''

    def hash(self, *data_list):
        '''
        Make a hash out of the given ``value``.

        :param `data_list`: the list of the data being hashed.
        :type  `data_list`: list of string
        :return:            the hashed data string
        '''

        hash_engine = hashlib.new('sha512')

        hash_engine.update(''.join(data_list))

        return hash_engine.hexdigest()

    def random_number(self):
        return random.randint(0,100000000000)

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
