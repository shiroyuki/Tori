"""
:Author: Juti Noppornpitak
"""

import re

from imagination.loader    import Loader
from tori.centre           import services
from tori.decorator.common import singleton
from tori.exception        import LoadedFixtureException

class Fixture(object):
    """
    Foundation of the council

    .. note:: this must be used at most once.

    .. warning:: this class is not tested.
    """
    def __init__(self, repository):
        self.__repository   = repository
        self.__loaded_kinds = {}
        self.__fixture_map  = {}
        self.__graphs       = {}

        self.__re_proxy = re.compile('^proxy/(?P<kind>[^/]+)/(?P<alias>.+)$')

    def set(self, kind, fixtures):
        """
        Define the fixtures.

        :param kind: a string represent the kind
        :type  kind: unicode|str
        :param fixtures: the data dictionary keyed by the alias
        :type  fixtures: dict

        .. code-block:: python

            fixture = Fixture()

            fixture.set(
                'council.security.model.Provider',
                {
                    'ldap': { 'name': 'ldap' }
                }
            )
            fixture.set(
                'council.user.model.User', {
                    'admin': { 'name': 'Juti Noppornpitak' }
                }
            )
            fixture.set(
                'council.security.model.Credential',
                {
                    'shiroyuki': {
                        'login':    'admin',
                        'user':     'proxy/council.user.model.User/admin',
                        'provider': 'proxy/council.security.model.Provider/ldap'
                    }
                }
            )

        """
        self.__fixture_map[kind] = fixtures

    @property
    def db(self):
        return self.__repository

    def load(self):
        for kind in self.__fixture_map.keys():
            self.load_fixtures(kind)

    def load_fixtures(self, kind):
        if kind in self.__loaded_kinds:
            return

        loader   = Loader(kind)
        fixtures = self.__fixture_map[kind]

        self.__loaded_kinds[kind] = loader
        self.__graphs[kind]       = []

        for id, fixture in fixtures.iteritems():
            fixture = self._prepare_fixture(fixture)
            entity  = loader.package(**fixture)

            self.db.post(entity)
            self.db.session.refresh(entity)

            fixtures[id] = entity

            self.__graphs[kind].append(entity)

    def _prepare_fixture(self, fixture):
        for key, value in fixture.iteritems():
            proxy_matches = self.__re_proxy.search(value)\
                if (isinstance(value, unicode) or isinstance(value, str))\
                else None

            if not proxy_matches:
                continue

            settings = proxy_matches.groupdict()

            self.load_fixtures(settings['kind'])

            fixture[key] = self.__fixture_map[settings['kind']][settings['alias']]

        return fixture
