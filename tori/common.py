# -*- coding: utf-8 -*-
"""
:Author: Juti Noppornpitak

This package contains classes and functions for common use.
"""
import codecs
import hashlib
import logging
import random

from .decorator.common import singleton

@singleton
class LoggerFactory(object):
    def __init__(self, default_level=None):
        self.__default_level = default_level or logging.WARNING
        self.__handler       = None
        self.__loggers       = {}

    def set_default_level(self, default_level):
        self.__default_level = default_level

        return self

    def make(self, name, level=None, show_time=True):
        level = level or self.__default_level

        if name in self.__loggers:
            return self.__loggers[name]

        logging_handler = logging.StreamHandler()
        logging_handler.setLevel(level)
        logging_handler.setFormatter(
            logging.Formatter(
                '%(levelname)s %(asctime)s %(name)s: %(message)s' if show_time else '%(levelname)s %(name)s: %(message)s',
                datefmt='%Y.%m.%d %H:%M:%S %Z'
            )
        )

        logger = logging.getLogger(name)
        logger.propagate = False

        logger.addHandler(logging_handler)
        logger.setLevel(level)

        self.__loggers[name] = logger

        return logger

def get_logger(name, level=None, show_time=True):
    return LoggerFactory.instance().make(name, level, show_time)

@singleton
class Enigma(object):
    """ Hashlib wrapper """

    def hash(self, *data_list):
        """
        Make a hash out of the given ``value``.

        :param `data_list`: the list of the data being hashed.
        :type  `data_list`: list of string
        :return:            the hashed data string
        """

        hash_engine = hashlib.new('sha512')
        data_list   = list(data_list)

        for i in range(len(data_list)):
            data_list[i] = codecs.encode(data_list[i], 'ascii')

        hash_engine.update(b''.join(data_list))

        return hash_engine.hexdigest()

    def random_number(self):
        return random.randint(0,100000000000)

class Finder(object):
    """ File System API Wrapper """

    def read(self, file_path, is_binary=False):
        """
        Read a file from *file_path*.

        By default, read a file normally. If *is_binary* is ``True``, the method will read in binary mode.
        """
        with codecs.open(file_path, 'rb' if is_binary else 'r', 'utf-8') as fp:
            file_content = fp.read()

        fp.close()

        return file_content
