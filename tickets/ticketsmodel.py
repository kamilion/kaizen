
__author__ = 'Kamilion@gmail.com'
########################################################################################################################
## Imports
########################################################################################################################

# Rethink imports
import rethinkdb as r

# Rethink configuration
#from app.config import rdb

# Import the remodel connection class so we can influence it's configuration, as we need to set the db and auth_key.
import remodel.connection
#remodel.connection.pool.configure(db=rdb['ticketsdb'],  # This db holds the 'billing' table.
# host=rdb['host'], port=rdb['port'], auth_key=rdb['auth_key'])
remodel.connection.pool.configure(db='kaizen', auth_key='158bcmcubed')



# Import the actual Model superclass.
from remodel.models import Model
from remodel.utils import create_tables, create_indexes

# Import regex support
import re

########################################################################################################################
## Tickets Class
########################################################################################################################

# This class represents a Ticket in RethinkDB.
class Ticket(Model):
    # Convenience method
    @classmethod
    def make(cls, source, name, email, phone, message):
        """
        Create a new Ticket entry.
        Remodel itself has a create() call, we need to provide data for it to store.
        @return: A Ticket object instantiated from the supplied data or None.
        """
        meta = {'source': source, 'name': name, 'email': email, 'phone': phone, 'updated_at': r.now()}
        print('TICKETSMODEL: Make: metadata: {}, message:\n{} '.format(meta, message))
        try:  # To make the database entry with the meta data.
            the_new_ticket = Ticket.create(meta=meta, message=message) 
        except KeyError:
            return None
        print('TICKETSMODEL: Make SUCCESS: metadata: {}, message:\n{} '.format(meta, message))
        return the_new_ticket

    # Convenience method
    @classmethod
    def get_ticket_from_email(cls, email):
        """
        Create a Ticket object from an email address
        @param email: The email address to request from RethinkDB
        @return: A Ticket object instantiated from the requested email address, or None.
        """
        if email == "None":
            return None
        else:
            try:
                theticket = Ticket.get(meta={'email': email})
                print('TICKETSMODEL: GetTicketFromEmail: {} found'.format(email))
                return theticket
            except KeyError:
                return None

    # Convenience method
    @classmethod
    def get_ticket_from_phone(cls, phone):
        """
        Create a Ticket object from a phone number
        @param email: The phone number to request from RethinkDB
        @return: A Ticket object instantiated from the requested phone number, or None.
        """
        if phone == "None":
            return None
        else:
            try:
                theticket = Ticket.get(meta={'phone': phone})
                print('TICKETSMODEL: GetTicketFromPhone: {} found'.format(phone))
                return theticket
            except KeyError:
                return None

    def __repr__(self):
        return '<Ticket {} Source: {} Name: {} Phone: {} Email: {}>'.format(
            self['id'], self['source'], self['name'], self['phone'], self['email'])


# Call this to populate the tables if they don't exist.
create_tables()
# Call this to populate the indexes if they don't exist.
create_indexes()
