
__author__ = 'Kamilion@gmail.com'
########################################################################################################################
## Imports
########################################################################################################################

# Flask-login imports
from flask.ext.login import LoginManager, UserMixin

# Third Party Libraries
import scrypt
import random

# yubikey imports
from yubico_client import Yubico
from yubico_client.otp import OTP
from app import config

yubico = Yubico(config.yubico_keys['client_id'], config.yubico_keys['secret_key'])

# Import the remodel connection class so we can influence it's configuration, as we need to set the db and auth_key.
import remodel.connection
remodel.connection.pool.configure(db=config.rdb['userdb'],  # This db holds the 'users' table.
 host=config.rdb['host'], port=config.rdb['port'], auth_key=config.rdb['auth_key'])

# Import the actual Model superclass.
from remodel.models import Model
from remodel.utils import create_tables, create_indexes

auth_debug = True

login_manager = LoginManager()

########################################################################################################################
## Login_Manager's required User Loader function
########################################################################################################################

@login_manager.user_loader
def load_user(user_uuid):
    """
    Instantiate a user object from a RethinkDB document UUID
    @param user_uuid: The RethinkDB UUID to request
    """
    if user_uuid != "None":
        try:
            return User.get(id=user_uuid)
        except KeyError:
            return None

########################################################################################################################
## ModelMixer Class
########################################################################################################################

class ModelMixer(UserMixin):
    """
    This reusable class needs to impliment the methods that flask-login expects:
    is_active, is_authenticated, is_anonymous, get_id, __eq__, __ne__
    """

    # Overrides UserMixin
    def get_id(self):
        """
        Gets a user's ID
        @return: True if the User was active, or False if the operation could not complete.
        """
        return unicode(self['id'])

    # Overrides UserMixin
    def is_active(self):
        """
        Check if a user entry is currently an Active User
        @return: True if the User was active, or False if the operation could not complete.
        """
        return self['active']

########################################################################################################################
## User Class
########################################################################################################################

class User(Model, ModelMixer):
    """
    This class will inherit the methods that flask-login expects:
    is_active, is_authenticated, is_anonymous, get_id, __eq__, __ne__
    We expect the following additional properties from remodel:
    self['email'], self['password'], self['admin'], self['superadmin'], self['auth_yubitoken']
    """
    has_one = ('UserProfile',)
    
    def is_admin(self):
        """
        Check if a user entry is currently an Admin User
        @return: True if the User was active, or False if the operation could not complete.
        """
        return self['admin']

    def is_superadmin(self):
        """
        Check if a user entry is currently an superadmin User
        @return: True if the User was active, or False if the operation could not complete.
        """
        return self['admin']

    def check_yubitoken(self, token):
        """
        Check the token of a user entry from a provided YubiCo token
        @param token: The token to check against a YubiCo OTP
        @return: True if the token was valid, or False if the operation could not complete.
        """
        try:
            if self['identity_yubico'] is not None:
                try:  # to verify the token against yubico servers
                    y = yubico.verify(token)
                    if auth_debug: print("AUTHMODEL: CheckYubiToken: Yubico SUCCESS for token: {}".format(token))
                except:  # If it doesn't work, just return none.
                    y = None
                    if auth_debug: print("AUTHMODEL: CheckYubiToken: Yubico FAILED for token: {}".format(token))
                # But if it did work, check against our stored token.
                if y and OTP(token).device_id == self['identity_yubico'][0:12]:
                    return True
        except KeyError:  # I really don't see how this could happen, but we'll check anyway.
            if auth_debug: print("AUTHMODEL: CheckYubiToken: Missing identity_yubico for: {}".format(self['email']))
            return False
        return False

    def check_password(self, input_pass):
        """
        Check the password of a user entry from a provided input password
        @param input_pass: The password to decode the secret with
        @return: True if the password was valid, or False if the operation could not complete.
        """
        try:
            result = scrypt.decrypt(  # Decode the crypto stream
                self['password'].decode('hex'),  # By pulling the hexed password from the DB
                input_pass.encode('ascii', 'ignore'),  # And passing in the password
                0.5)  # Take half a second to do this.
            if auth_debug: print("AUTHMODEL: CheckPassword: SUCCESS InputPass: {}".format(input_pass))
            return True  # We don't check our cookie above, but it matches.
        except scrypt.error:
            if auth_debug: print("AUTHMODEL: CheckPassword: FAILED InputPass: {}".format(input_pass))
            return False  # Because you get 'password is incorrect' if it does not.

    def change_password(self, input_pass):
        """
        Change the password of a user entry from an new password
        @param input_pass: The password to register with RethinkDB
        @return: True if the record was updated, or False if the operation could not complete.
        """
        try:
            new_password = scrypt.encrypt(
                ''.join(chr(random.randint(0, 255)) for i in range(64)),  # Store a Random Cookie
                input_pass.encode('ascii', 'ignore'),  # Assure the password is ascii.
                0.5  # How long should we take?
            ).encode('hex')  # Store the completed password as hex
            if auth_debug: print("AUTHMODEL: SetNewPassword: InputPass: {}".format(input_pass))
            self['password'] = new_password
            self.save()  # Aiee, better error checking here, return false if this fails.
            return True  # We don't check our cookie above, but it matches.
        except scrypt.error:
            return False  # Because you get 'password is incorrect' if it does not.

    # Convenience method
    @classmethod
    def make(cls, email, input_pass):
        """
        Create a new user entry from an email address and password
        Remodel itself has a create() call, we need a crypted password for it to store.
        @param email: The email address to register with RethinkDB
        @param input_pass: The password to register with RethinkDB
        @return: A User object instantiated from the requested email address, or None.
        """
        try:  # To make a crypted password
            new_password = scrypt.encrypt(
                ''.join(chr(random.randint(0, 255)) for i in range(64)),  # Store a Random Cookie
                input_pass.encode('ascii', 'ignore'),  # Assure the password is ascii.
                0.5  # How long should we take?
            ).encode('hex')  # Store the completed password as hex
            if auth_debug: print("AUTHMODEL: SetNewPassword: InputPass: {}".format(input_pass))
        except scrypt.error:
            return None  # Because you get 'password is incorrect' if it does not.

        try:  # To make the database entry with the crypted password
            the_new_user = User.create(email=email, password=new_password, 
                                           active=True, admin=False, superadmin=False)
        except KeyError:
            return None

        return the_new_user  # We don't check our scrypt cookie above, but it matches.


    # Convenience method
    @classmethod
    def get_user_from_email(cls, email):
        """
        Create a user object from an email address
        @param email: The email address to request from RethinkDB
        @return: A User object instantiated from the requested email address, or None.
        """
        if email == "None":
            return None
        else:
            try:
                theuser = User.get(email=email)
                if auth_debug: print('AUTHMODEL: GetUserFromEmail: {} found'.format(email))
                return theuser
            except KeyError:
                return None

    # Convenience method
    @classmethod
    def get_user_from_yubitoken(cls, yubitoken):
        """
        Create a user object from an yubikey token
        @param yubitoken: The YubiCo Identity to request from RethinkDB
        @return: A User object instantiated from the requested YubiCo Identity, or None.
        """
        if yubitoken == "None":
            return None
        else:
            try:
                theuser = User.get(identity_yubico=yubitoken[0:12])
                if auth_debug: print('AUTHMODEL: GetUserFromYubiToken: {} matches for user {}'.format(
                                                                     yubitoken, theuser['email'])) 
                return theuser
            except KeyError:
                return None


    def __repr__(self):
        return '<User {} Superadmin: {} Admin: {}>'.format(
            self['email'], self['superadmin'], self['admin'])

class UserProfile(Model):
    """
    This class will not inherit the methods that flask-login expects.
    """
    belongs_to = ('User',)

# Call this to populate the tables if they don't exist.
#create_tables()
# Call this to populate the indexes if they don't exist.
#create_indexes()
