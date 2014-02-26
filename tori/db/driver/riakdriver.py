from riak import RiakClient
from tori.db.manager import register_driver as driver
from tori.db.driver.interface import DriverInterface

@driver('mongodb')
class Driver(DriverInterface):
    def db(self, name):
        return None
    
    def collection(self, name):
        return self._client.bucket(name)
    
    def insert(self, collection_name, data):
        riak_object = self.collection(collection_name).new(data=inserted_data)
        riak_object.store()

        return riak_object.key

    def update(self, criteria_or_id, updated_data):
        # Note: criteria_or_id can only be a key due to backend limitation.
        riak_object = self.get(criteria_or_id)

        if not riak_object:
            raise ObjectNotFoundError('Unable to update the object.')

        for property_name in updated_data:
            riak_object.data[property_name] = updated_data[property_name]

        riak_object.store()

    def delete(self, criteria_or_id):
        # Note: criteria_or_id can only be a key due to backend limitation.
        riak_object = self.get(criteria_or_id)

        if not riak_object:
            return False

        riak_object.delete()

        return True

    def connect(self, config):
        self.client = RiakClient(config)

    def disconnect(self): raise NotImplemented()