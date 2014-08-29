# -*- coding: utf-8 -*-
# Obsolete test as the support for indexing will be dropped in 3.1.
from ft.db.dbtestcase import DbTestCase
from tori.db.driver.mongodriver import Driver
from tori.db.session import Session
from tori.db.common import ProxyObject
from tori.db.criteria import Criteria, Order
from tori.db.uow import Record
from tori.db.entity import entity, Index
from tori.db.mapper import link, CascadingType, AssociationType

@entity
class Author(object):
    def __init__(self, name):
        self.name = name

@link(mapped_by='author', target=Author, association=AssociationType.ONE_TO_ONE)
@entity(
    indexes=[
        Index({'name': Order.ASC, 'language': Order.ASC})
    ]
)
class Series(object):
    def __init__(self, name, published_in, author):
        self.name     = name
        self.author   = author
        self.published_in = published_in

class TestFunctional(DbTestCase):
    base_index_count   = 2
    manual_index_count = 4
    auto_index_count   = 5

    def test_auto_index(self):
        repository = self.session.repository(Series)

        repository.auto_index(True)

        samples = [
            {
                'criteria': repository.new_criteria().order('name', Order.DESC),
                'expected_name': 'RDG Red Data Girl',
                'expected_list_index': 0,
                'expected_db_index_count': self.auto_index_count - 1
            },
            {
                'criteria': repository.new_criteria().order('published_in').order('name', Order.DESC),
                'expected_name': 'Library War',
                'expected_list_index': 2,
                'expected_db_index_count': self.auto_index_count - 1
            },
            {
                'criteria': repository.new_criteria().where('published_in', 2006).order('name', Order.DESC).order('published_in'),
                'expected_name': 'Library War',
                'expected_list_index': 0,
                'expected_db_index_count': self.auto_index_count - 1
            }
        ]

        sample_count = 0

        for sample in samples:
            self._reset_db(self.__data_provider())

            sample_count += 1
            series_list = repository.find(sample['criteria'])

            self.assertEqual(
                sample['expected_name'],
                series_list[sample['expected_list_index']].name,
                'Sample #{} > Assertion #1'.format(sample_count)
            )

            self.assertEqual(
                sample['expected_db_index_count'],
                self.driver.index_count(),
                'Sample #{} > Assertion #2'.format(sample_count)
            )

    def __data_provider(self):
        return [
            {
                'class': Author,
                'fixtures':   [
                    {'_id': 1, 'name': 'Noriko Ogiwara'},
                    {'_id': 2, 'name': 'Honobu Yonezawa'},
                    {'_id': 3, 'name': 'Tetsurō Sayama'},
                    {'_id': 4, 'name': 'Hiro Arikawa'},
                    {'_id': 5, 'name': 'Nishio Ishin'}
                ]
            },
            {
                'class': Series,
                'fixtures':   [
                    {
                        '_id': 1,
                        'name': 'RDG Red Data Girl',
                        'language': 'Japanese',
                        'published_in': 2012,
                        'author': 1
                    },
                    {
                        '_id': 2,
                        'name': 'Hyōka',
                        'language': 'Japanese',
                        'published_in': 2001,
                        'author': 2
                    },
                    {
                        '_id': 3,
                        'name': 'From Up on Poppy Hill',
                        'language': 'Japanese',
                        'published_in': 1980,
                        'author': 3
                    },
                    {
                        '_id': 4,
                        'name': 'Library War',
                        'language': 'Japanese',
                        'published_in': 2006,
                        'author': 4
                    },
                    {
                        '_id': 5,
                        'name': 'Bakemonogatari',
                        'language': 'Japanese',
                        'published_in': 2006,
                        'author': 5
                    }
                ]
            }
        ]