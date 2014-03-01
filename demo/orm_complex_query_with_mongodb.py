from tori.db.manager import ManagerFactory
from tori.db.entity import entity, Entity

@entity
class BannedUser(object):
    def __init__(self, name):
        self.name = name

@entity
class User(Entity):
    def __init__(self, **attributes):
        assert 'name' in attributes

        for name in attributes:
            self.__setattr__(name, attributes[name])

def query(user_repository, banned_user_repository):
    banned_users_with_on_demand_filter = banned_user_repository.on_demand_filter()

    primary_criteria = user_repository.new_criteria('u')

    # to notify the criteria for possible sub queries.
    primary_criteria.join('u.country', 'c')

    mr_countries_with_age_restriction = c.new_map_reducer() # tori.db.mr.MapReducer
    mr_countries_with_age_restriction.first('u.age <= :age') # First condition
    mr_countries_with_age_restriction.then('u.country.name in :arc_list') # Next condition

    mr_countries_with_no_restriction  = c.new_map_reducer() # tori.db.mr.MapReducer
    mr_countries_with_no_restriction.then('u.country.name in :nrc_list')

    mr_countries = c.new_map_reducer() # tori.db.mr.MapReducer
    mr_countries.first(mr_countries_with_age_restriction) # First condition with the first compound map reducer.
    mr_countries.if_not_then(mr_sub) # semantically means "OR" with the second compound map reducer.

    mr = c.new_map_reducer() # tori.db.mr.MapReducer
    mr.first(mr_countries)
    mr.then('u.name not in :banned_list')

    # Define the parameters
    mr.define(
        age = 13,
        arc_list = ['United States', 'Canada'],
        nrc_list = ['Japan', 'Thailand'],
        banned_list = banned_users_with_on_demand_filter # Use the on-demand filter to use the multi-threading queries.
    )

    primary_criteria.map_reduce = mr # set the primary map reducer.

    return user_repository.filter(primary_criteria)

mf = ManagerFactory()
mf.connect('mongodb://localhost/t3demo')

user_repository        = mf.repository(User)
banned_user_repository = mf.repository(BannedUser)

print(query(user_repository, banned_user_repository))