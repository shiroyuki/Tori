from time import time

class DependencyNode(object):
    """ Dependency Node

        This is designed to be bi-directional to maximize flexibility on
        traversing the graph.
    """
    def __init__(self):
        self.created_at     = int(time() * 1000000)
        self.adjacent_nodes = set()
        self.reverse_edges  = set()
        self.walked         = False

    def connect(self, other):
        self.adjacent_nodes.add(other)
        other.reverse_edges.add(self)

    def _disavow_connection(self, node):
        return False

    @property
    def score(self):
        score = 0

        for node in self.reverse_edges:
            if self._disavow_connection(node):
                continue

            score += 1

        return score

    def __eq__(self, other):
        return self.created_at == other.created_at

    def __ne__(self, other):
        return self.created_at != other.created_at

    def __lt__(self, other):
        return self.score < other.score

    def __le__(self, other):
        return self.score <= other.score

    def __gt__(self, other):
        return self.score > other.score

    def __ge__(self, other):
        return self.score >= other.score

    def __hash__(self):
        return self.created_at

    def __repr__(self):
        return '<DependencyNode for {}, {}>'.format(self.object_id, self.score)

class DependencyManager(object):
    @staticmethod
    def get_order(dependency_map):
        # After constructing the dependency graph (as a supposedly directed acyclic
        # graph), do the topological sorting from the dependency graph.
        final_order = []

        for id in dependency_map:
            node = dependency_map[id]

            DependencyManager._retrieve_dependency_order(node, final_order)

        return final_order

    @staticmethod
    def _retrieve_dependency_order(node, priority_order):
        if node.walked:
            return

        node.walked = True

        initial_order = list(node.adjacent_nodes)

        for adjacent_node in initial_order:
            DependencyManager._retrieve_dependency_order(adjacent_node, priority_order)

        if node not in priority_order:
            priority_order.append(node)