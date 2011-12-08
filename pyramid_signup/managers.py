import cryptacular.bcrypt
crypt = cryptacular.bcrypt.BCRYPTPasswordManager()

from pyramid_signup.models import User
from pyramid_signup.lib import get_session

class UserManager(object):
    def __init__(self, request):
        self.request = request
        self.session = get_session(request)

    def get_by_email(self, email):
        return self.session.query(User).filter(User.email == email).first()

    def get_by_username(self, username):
        return self.session.query(User).filter(User.username == username).first()

    def get_by_activation(self, activation):
        user = self.session.query(User).filter(User.activation == activation).first()
        return user

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
