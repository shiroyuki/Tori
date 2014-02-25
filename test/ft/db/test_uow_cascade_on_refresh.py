# -*- coding: utf-8 -*-
from ft.db.dbtestcase import DbTestCase
from tori.db.session import Session
from tori.db.entity  import entity
from tori.db.mapper  import link, CascadingType, AssociationType

@link(
    mapped_by='region',
    target='ft.db.test_uow_cascade_on_refresh.Region',
    association=AssociationType.MANY_TO_ONE,
    cascading=[CascadingType.REFRESH, CascadingType.PERSIST]
)
@entity('countries')
class Country(object):
    def __init__(self, name, region):
        self.name   = name
        self.region = region

@link(
    mapped_by='countries',
    target='ft.db.test_uow_cascade_on_refresh.Country',
    inverted_by='region',
    association=AssociationType.ONE_TO_MANY,
    cascading=[CascadingType.REFRESH],
    read_only=True
)
@entity('regions')
class Region(object):
    def __init__(self, name, countries=[]):
        self.name      = name
        self.countries = countries

class TestFunctional(DbTestCase):
    def setUp(self):
        self._setUp()

        self._reset_db([
            {
                'class': Region,
                'fixtures': [
                    {'_id': 1, 'name': 'Asia'},
                    {'_id': 2, 'name': 'Europe'},
                    {'_id': 3, 'name': 'North America'}
                ]
            },
            {
                'class': Country,
                'fixtures': [
                    {'_id': 1, 'region': 3, 'name': 'Canada'},
                    {'_id': 2, 'region': 2, 'name': 'England'},
                    {'_id': 3, 'region': 1, 'name': 'Japan'},
                    {'_id': 4, 'region': 1, 'name': 'Thailand'}
                ]
            }
        ])

    def test_cascade_from_owning_side(self):
        collection = self.session.collection(Region)
        japan = self.session.collection(Country).get(3)

        self.assertEqual('Japan', japan.name)
        self.assertEqual('Asia', japan.region.name)

        # At this point, Region 1 is loaded into the memory.
        # Bypass the identity map and then update the data manually.
        collection.driver.update(collection.name, {'_id': 1}, {'$set': {'name': 'Asia and Oceanic'}})

        # Now, try to persist the data.
        japan.name = u'日本'

        self.session.persist(japan)
        self.session.flush()

        # Confirm that only the name of the country is updated
        self.assertEqual(u'日本', japan.name)
        self.assertEqual('Asia', japan.region.name)

        # Refresh the entity
        self.session.refresh(japan)

        # Confirm that only the name of the region is updated after refreshing
        self.assertEqual(u'日本', japan.name)
        self.assertEqual('Asia and Oceanic', japan.region.name)

    def test_cascade_from_inverted_side(self):
        collection = self.session.collection(Region)
        europe = self.session.collection(Region).get(2)

        self.assertEqual('Europe', europe.name)
        self.assertEqual('England', europe.countries[0].name)

        # At this point, Region 1 is loaded into the memory.
        # Bypass the identity map and then update the data manually.
        collection.driver.update(collection.name, {'_id': 2}, {'$set': {'name': 'United Kingdom of Great Britain and Ireland'}})

        # Now, try to persist the data.
        europe.name = 'Europian Union'

        self.session.persist(europe)
        self.session.flush()

        # Confirm that only the name of the country is updated
        self.assertEqual('Europian Union', europe.name)
        self.assertEqual('England', europe.countries[0].name)

        # Refresh the entity
        self.session.refresh(europe)

        # Confirm that refreshing doesn't work with reverse-mapping properties.
        self.assertEqual('Europian Union', europe.name)
        self.assertEqual('England', europe.countries[0].name)