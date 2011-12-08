import cryptacular.bcrypt
crypt = cryptacular.bcrypt.BCRYPTPasswordManager()

from pyramid_signup.models import User
from pyramid_signup.interfaces import ISUSession

class UserManager(object):
    def __init__(self, request):
        self.request = request
        self.session = self.get_session()

    def get_session(self):
        session = self.request.registry.getUtility(ISUSession)

        return session

    def get_by_username(self, username):
        return self.session.query(User).filter(User.username == username).first()

    def get_by_pk(self, pk):
        """Gets an object by its primary key"""
        return self.session.query(User).filter(User.pk == pk).first()


    def get_user(self, username, password):
        user = self.get_by_username(username)

        if not user:
            return None

        valid = crypt.check(user.password, password + user.salt)

        if valid:
            return user
