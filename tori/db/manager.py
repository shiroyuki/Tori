import re
from bson.objectid import ObjectId
from tori.db.driver.interface import DriverInterface
from tori.db.session import Session
from tori.db.exception import InvalidUrlError, UnknownDriverError

def register_driver(protocol):
    print(protocol)
    def inner_decorator(ctype):
        print(ctype)
        ManagerFactory.protocol_to_driver_map[protocol] = ctype

        return ctype

    return inner_decorator

class ManagerFactory(object):
    protocol_to_driver_map = {}

    def __init__(self):
        self._re_url = re.compile('(?P<protocol>[a-zA-Z]+)://(?P<address>.+)')

    def analyze_url(self, url):
        index = 0
        connection_info = {}

        matches = self._re_url.match(url)

        if matches:
            return matches.groupdict()

        raise InvalidUrlError('Invalid URL to {}'.format(url))

    def driver(self, url):
        config = self.analyze_url(url)

        if not config:
            raise UnknownDriverError('Unable to connect to {} due to invalid configuration'.format())

        if config['protocol'] in ManagerFactory.protocol_to_driver_map:
            return ManagerFactory.protocol_to_driver_map[protocol]

        raise UnknownDriverError('Unable to connect to {}'.format(url))

    def connect(self, url):
        pass

class Manager(object):
    """ Entity Manager

        :param name: the name of the database
        :type  name: str
        :param driver: the driver interface
        :type  driver: tori.db.driver.interface.DriverInterface
    """
    def __init__(self, name, driver):
        assert isinstance(driver, DriverInterface), 'The given driver must implement DriverInterface.'
        self._name        = name
        self._driver      = driver
        self._session_map = {}
        self._driver      = driver

        self._driver.database_name = name

    @property
    def driver(self):
        """ Driver API

        :rtype: tori.db.driver.interface.DriverInterface
        """
        return self._driver

    def open_session(self, id=None, supervised=False):
        """ Open a session

            :param id: the session ID
            :param supervised: the flag to indicate that the opening session
                               will be observed and supervised by the manager.
                               This allows the session to be reused by multiple
                               components. However, it is not **thread-safe**.
                               It is disabled by default.
            :type  supervised: bool
        """
        if not supervised:
            return Session(self.driver)

        if not id:
            id = ObjectId()

        if id in self._session_map:
            return self._session_map[id]

        session = Session(self.driver)

        if supervised:
            self._session_map[id] = session

        return session

    def close_session(self, id_or_session):
        """ Close the managed session

            .. warning::

                This method is designed to bypass errors when the given ID is
                unavailable or already closed.
        """
        id = id_or_session.id if isinstance(id_or_session, Session) else id_or_session

        if not id or id not in self._session_map:
            return

        del self._session_map[id]
