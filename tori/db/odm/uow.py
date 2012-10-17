'''
:Author: Juti Noppornpitak <jnopporn@shiroyuki.com>
:Availability: DEV
:Stability: Experimental
'''

from imagination.decorator.validator import restrict_type

class UnitOfWork(object):
    '''
    Unit Of Work for MongoDB

    This class is to enable transaction support for MongoDB which has no native
    support for transaction.

    The primary responsibilities of this class are:
    * Manage transactions.
    * Order the database inserts, deletes, and updates.
    * Prevent duplicate updates. Inside a single usage of a Unit of Work object,
      different parts of the code may mark the same Invoice object as changed,
      but the Unit of Work class will only issue a single UPDATE command to the
      database.
    '''
    def mark_dirty(document):
        pass

    def mark_new(document):
        pass

    def mark_deleted(document):
        pass

    def commit():
        pass

    def rollback():
        pass
