from unittest import TestCase
from tori.db.common import ProxyObject
from tori.db.entity import entity
from tori.db.exception import ReadOnlyProxyException
from tori.db.manager import Manager
from tori.db.mapper import link, CascadingType, AssociationType

@link(
    mapped_by='destinations',
    inverted_by='origin',
    target='testcase.test_db_mapper_bidirectional_mapping.Destination',
    association=AssociationType.ONE_TO_MANY,
    cascading=[CascadingType.PERSIST, CascadingType.DELETE]
)
@entity('test_tori_db_mapper_bidirectional_mapping_origin')
class Origin(object):
    def __init__(self, name, destinations):
        self.name         = name
        self.destinations = destinations

@link(
    mapped_by='origin',
    target=Origin,
    association=AssociationType.MANY_TO_ONE,
    cascading=[CascadingType.PERSIST, CascadingType.DELETE]
)
@entity('test_tori_db_mapper_bidirectional_mapping_destination')
class Destination(object):
    def __init__(self, name, origin):
        self.name   = name
        self.origin = origin

class TestDbManager(TestCase):
    em = Manager('test_tori_db_manager')

    def setUp(self):
        self.session = self.em.open_session()

        for collection in self.session.collections:
            collection._api.remove() # Reset the database

    def tearDown(self):
        self.em.close_session(self.session)

    def test_reverse_mapping_normal_path_call_get(self):
        self.__inject_data()

        origin = self.session.collection(Origin).filter_one({'name': 'origin'})

        self.assertIsNotNone(origin)
        self.assertEquals(2, len(origin.destinations))
        self.assertIsInstance(origin.destinations[0], ProxyObject)
        self.assertEquals('a', origin.destinations[0].name)

    def test_reverse_mapping_normal_path_call_put(self):
        self.__inject_data()

        collection = self.session.collection(Origin)

        origin = collection.filter_one({'name': 'origin'})

        try:
            origin.destinations[0].name = 'Bangkok'
            self.assertTrue(False, 'The reverse proxy is always read-only.')
        except ReadOnlyProxyException as exception:
            pass

    def __inject_data(self):
        api = self.session.collection(Origin)._api

        origin_id = api.insert({'name': 'origin'})

        api = self.session.collection(Destination)._api

        a_id = api.insert({'origin': origin_id, 'name': 'a'})
        b_id = api.insert({'origin': origin_id, 'name': 'b'})