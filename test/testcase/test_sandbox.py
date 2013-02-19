from unittest import TestCase
from tori.db.common import ProxyObject

try:
    from unittest.mock import Mock, MagicMock # Python 3.3
except ImportError as exception:
    from mock import Mock, MagicMock # Python 2.7

from tori.db.document import document
from tori.db.manager import Manager
from tori.db.mapper import link, CascadingType, AssociationType

@document
class Computer(object):
    def __init__(self, name):
        self.name = name

@link('computer', Computer, association_type=AssociationType.ONE_TO_ONE)
@link('delegates', association_type=AssociationType.ONE_TO_MANY, cascading=[CascadingType.PERSIST, CascadingType.DELETE])
@document
class Developer(object):
    def __init__(self, name, computer=None, delegates=[]):
        self.name      = name
        self.computer  = computer
        self.delegates = delegates

class TestSandbox(TestCase):
    def setUp(self):
        self.em  = Manager('tori_test', document_types=[Developer, Computer])

        for collection in self.em.collections:
            collection._api.remove() # Reset the database

    def test_sandbox(self):
        return

    def __debug_graph(self, graph):
        print('----- Begin -----')

        for id in graph:
            node = graph[id]

            print('[{} {} {}]'.format(node.record.entity.name, node.score, node.record.entity.id))

            for other in node.adjacent_nodes:
                print('  --> [{} {} {}]'.format(other.record.entity.name, other.score, node.record.entity.id))

            for other in node.reverse_edges:
                print('  <-- [{} {} {}]'.format(other.record.entity.name, other.score, node.record.entity.id))
        print('----- End -----')