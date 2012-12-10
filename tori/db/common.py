"""
Common Module
=============

:Author: Juti Noppornpitak <jnopporn@shiroyuki.com>
:Stability: Stable
"""

from time import time

from tori.common import Enigma

class GuidGenerator(object):
    """Simply GUID Generator"""
    def __init__(self):
        self.counter     = 0
        self.known_guids = []

    def generate(self):
        """Generate the GUID

        :return: Global unique identifier within the scope of the generator
        :rtype: str
        """
        self.counter = self.counter + 1

        guid = None

        while guid in self.known_guids or not guid:
            guid = self._generate()

        return guid

    def _generate(self):
        """Generate an identifier

        :return: Global unique identifier within the scope of the generator
        :rtype: str
        """
        return u'{}.{}'.format(time(), self.counter)

class HashGuidGenerator(GuidGenerator):
    """Hash-type GUID Generator"""

    def __init__(self):
        GuidGenerator.__init__(self)

        self.enigma = Enigma.instance()

    def _generate(self):
        return self.enigma.hash(super(self, GuidGenerator)._generate())