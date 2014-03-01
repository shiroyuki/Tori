from tori.db.manager import ManagerFactory
from tori.db.entity import entity, Entity

@entity
class User(Entity):
    def __init__(self, **attributes):
        assert 'name' in attributes

        for name in attributes:
            self.__setattr__(name, attributes[name])

def query(user_repository):
    primary_criteria = user_repository.new_criteria('u')

    # to notify the criteria for possible sub queries.
    primary_criteria.join('u.country', 'c')

    mr = c.new_map_reducer() # tori.db.mr.MapReducer
    mr.first('u.indice in :filtered_indice') # "indice" is a virtual property which is only allowed to used for query in Riak 1.4.x. When Riak 2.0 is released with a integrated Apache Solr, the query will be able to take a complex instruction.

    # Define the parameters
    mr.define(
        filtered_indice = ['authorized']
    )

    primary_criteria.map_reduce = mr # set the primary map reducer.

    return user_repository.filter(primary_criteria)

mf = ManagerFactory()
mf.connect('riak://localhost/')

user_repository = mf.repository(User)

print(query(user_repository))