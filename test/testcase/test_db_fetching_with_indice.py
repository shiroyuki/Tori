# -*- coding: utf-8 -*-

from unittest import TestCase
from pymongo import Connection
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
        Index(['published_in'])
    ]
)
class Series(object):
    def __init__(self, name, published_in, author):
        self.name     = name
        self.author   = author
        self.published_in = published_in

class TestDbFetchingWithIndice(TestCase):
    connection = Connection()
    session    = Session('test', connection['db_fetching_with_indice'])
    base_index_count   = 2
    manual_index_count = 2
    auto_index_count   = 4

    def setUp(self):
        self.indexes = self.session.db['system.indexes']

        authors = self.session.repository(Author)
        series  = self.session.repository(Series)

        data_list = [
            {
                'repository': authors,
                'fixtures':   [
                    {'_id': 1, 'name': 'Noriko Ogiwara'},
                    {'_id': 2, 'name': 'Honobu Yonezawa'},
                    {'_id': 3, 'name': 'Tetsurō Sayama'},
                    {'_id': 4, 'name': 'Hiro Arikawa'},
                    {'_id': 5, 'name': 'Nishio Ishin'}
                ]
            },
            {
                'repository': series,
                'fixtures':   [
                    {
                        '_id': 1,
                        'name': 'RDG Red Data Girl',
                        'published_in': 2012,
                        'author': 1
                    },
                    {
                        '_id': 2,
                        'name': 'Hyōka',
                        'published_in': 2001,
                        'author': 2
                    },
                    {
                        '_id': 3,
                        'name': 'From Up on Poppy Hill',
                        'published_in': 1980,
                        'author': 3
                    },
                    {
                        '_id': 4,
                        'name': 'Library War',
                        'published_in': 2006,
                        'author': 4
                    },
                    {
                        '_id': 5,
                        'name': 'Bakemonogatari',
                        'published_in': 2006,
                        'author': 5
                    }
                ]
            }
        ]

        for data in data_list:
            repository = data['repository']

            repository._api.drop_indexes()
            repository._api.drop()

            for fixture in data['fixtures']:
                repository._api.insert(fixture)

    def test_auto_index_on_normal_sorting(self):
        repository = self.session.repository(Series)
        criteria   = Criteria()

        criteria.order('name', Order.DESC)

        series_list = repository.find(criteria)

        self.assertEqual('RDG Red Data Girl', series_list[0].name)
        self.assertEqual(self.manual_index_count, self.indexes.count())

    def test_auto_index_on_combined_sorting(self):
        repository = self.session.repository(Series)
        criteria   = Criteria()

        criteria.order('published_in')
        criteria.order('name', Order.DESC)

        series_list = repository.find(criteria)

        self.assertEqual(4, series_list[2].id)
        self.assertEqual(self.manual_index_count, self.indexes.count())

    def test_auto_index_on_normal_sorting_with_predefined_indexes(self):
        repository = self.session.repository(Series)
        criteria   = Criteria()

        criteria.where('published_in', 2006)
        criteria.order('name', Order.DESC)

        series_list = repository.find(criteria)
        
        self.assertEqual('Library War', series_list[0].name)
        self.assertEqual(self.manual_index_count, self.indexes.count())