from ft.db.dbtestcase import DbTestCase
from passerine.db.common import ProxyObject
from passerine.db.entity import entity
from passerine.db.exception import ReadOnlyProxyException
from passerine.db.mapper import link, CascadingType, AssociationType

@link(
    mapped_by='destinations',
    inverted_by='origin',
    target='ft.db.test_mapper_bidirectional_mapping.Destination',
    association=AssociationType.ONE_TO_MANY,
    cascading=[CascadingType.PERSIST, CascadingType.DELETE]
)
@entity('o')
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
@entity('d')
class Destination(object):
    def __init__(self, name, origin):
        self.name   = name
        self.origin = origin

class TestFunctional(DbTestCase):
    def setUp(self):
        self._setUp()
        self._reset_db(self.__data_provider())
        
    def test_reverse_mapping_normal_path_call_get(self):
        origin = self._find_one_by_name(Origin, 'origin')

        self.assertIsNotNone(origin)
        self.assertEquals(2, len(origin.destinations))
        self.assertIsInstance(origin.destinations[0], ProxyObject)
        self.assertEquals('a', origin.destinations[0].name)

    def test_reverse_mapping_normal_path_call_put(self):
        origin = self._find_one_by_name(Origin, 'origin')

        try:
            origin.destinations[0].name = 'Bangkok'
            self.assertTrue(False, 'The reverse proxy is always read-only.')
        except ReadOnlyProxyException as exception:
            pass

    def __data_provider(self):
        return [
            {
                'class': Origin,
                'fixtures': [
                    {'_id': 1, 'name': 'origin'}
                ]
            },
            {
                'class': Destination,
                'fixtures': [
                    {'_id': 1, 'origin': 1, 'name': 'a'},
                    {'_id': 2, 'origin': 1, 'name': 'b'}
                ]
            }
        ]