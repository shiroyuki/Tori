# -*- coding: utf-8 -*-

'''
:Author: Juti Noppornpitak

Common module manages sessions with the session ID, key and value.

.. warning:: This module is not tested.
'''

from time import time

from sqlalchemy       import Column
from sqlalchemy.types import Integer, PickleType, String

from .centre      import settings as AppSettings
from .common      import Console, Enigma
from .exception   import *
from .rdb         import Entity
from .service.rdb import EntityService, RelationalDatabaseService

class DbSessionEntity(Entity):
    '''
    DB Session Entity is made to be compatible with any
    SQLAlchemy-based database session controller.
    '''

    __tablename__ = 'tori_session'

    id         = Column(Integer, primary_key=True)
    session_id = Column(String(128), index=True)
    key        = Column(String(128), index=True)
    content    = Column(PickleType)

    def __init__(self, session_id, key, content):
        self.session_id = session_id
        self.key        = key
        self.content    = content

class AbstractSession(object):
    ''' Abstract Session Controller '''

    def delete(self, id, key):
        '''
        Delete a session key.

        :param `id`:  session ID
        :param `key`: session data key

        .. note:: This method is not implemented in :class:`AbstractSession`.
        '''
        raise FutureFeature

    def generate(self):
        '''
        Generate the session ID

        :return: Session ID as a string
        '''
        if 'cookie_secret' not in AppSettings:
            raise SessionError, 'This session component could not not be initialized.'

        session_id = None

        while not session_id or self.registered(session_id):
            session_id = Enigma.instance().hash(
                '%s/%s' % (AppSettings['cookie_secret'], time())
            )

        return session_id

    def get(self, id, key, auto_close=True):
        '''
        Set the given content to a session key.

        :param `id`:  session ID
        :param `key`: session data key
        :return:      session data content

        .. note:: This method is not implemented in :class:`AbstractSession`.
        '''
        raise FutureFeature

    def has(self, id, key):
        '''
        Set the given content to a session key.

        :param `id`:  session ID
        :param `key`: session data key
        :return:      ``True`` if there exists the data.
        '''
        return self.get(session_id, key) is not None

    def registered(self, id):
        '''
        Set the given content to a session key.

        :param `id`: session ID
        :return:     ``True`` if the session ID is registered.

        .. note:: This method is not implemented in :class:`AbstractSession`.
        '''
        raise FutureFeature

    def set(self, id, key, content):
        '''
        Set the given content to a session key.

        :param `id`:      session ID
        :param `key`:     session data key
        :param `content`: session data content
        :return:          session data content

        .. note:: This method is not implemented in :class:`AbstractSession`.
        '''
        raise FutureFeature

class DbSession(AbstractSession):
    '''
    Session Controller using SQLAlchemy's ORM

    :param `url`: SQLAlchemy-compatible connection URL

    .. note::

        This is based on :class:`AbstractSession`. All non-implementing methods
        in the parent class are implemented. This is only compatible with
        :class:`DbSessionEntity`.

    '''

    def __init__(self, url='sqlite:///:memory:'):
        Console.log('tori.session.DbSession: %s' % url)

        self.db         = RelationalDatabaseService(url)
        self.entities   = EntityService(self.db, DbSessionEntity)
        self.db_session = None

    def session(self):
        if not self.db_session:
            self.db_session = self.db.session()

        return self.db_session

    def base_filter(self, id):
        return self.session().\
            query(DbSessionEntity).\
            filter(DbSessionEntity.session_id==id)

    def commit(self):
        if not self.db_session:
            return

        self.db_session.commit()
        self.close()

    def close(self):
        if not self.db_session:
            return

        self.db_session.close()

        self.db_session = None

    def delete(self, id, key):
        data = self.base_filter(id).\
            filter(DbSessionEntity.key==key).\
            first()

        if not data:
            self.close()
            return

        self.session().delete(data)
        self.commit()

    def get(self, id, key):
        data = self.base_filter(id).\
            filter(DbSessionEntity.key==key).\
            first()

        self.close()

        return data and data.content or None

    def registered(self, id):
        data = self.base_filter(id).all()

        self.close()

        return len(data) > 0

    def set(self, id, key, content):
        data = self.base_filter(id).\
            filter(DbSessionEntity.key==key).\
            first()

        if not data:
            data = DbSessionEntity(id, key, content)
            self.session().add(data)

        data.content = content

        self.commit()
