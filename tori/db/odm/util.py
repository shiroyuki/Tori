from time import time

from tori.common import Enigma

class GuidGenerator(object):
    counter = 0

    def generate(self):
        self.counter = self.counter + 1

        guid = '{}:{}'.format(
            time(),
            self.counter
        )

        return guid

class HashGuidGenerator(object):
    def __init__(self):
        self.enigma = Enigma.instance()

    def generate(self):
        guid = self.enigma.hash('{}:{}'.format(
            time(),
            self.enigma.random_number() % 1024
        ))

        return guid