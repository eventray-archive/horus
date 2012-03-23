from sqlalchemy import or_

import cryptacular.bcrypt

from pyramid_signup.models import User
from pyramid_signup.models import UserGroup
from pyramid_signup.models import Activation
from pyramid_signup.models import Organization
from pyramid_signup.lib import get_session

crypt = cryptacular.bcrypt.BCRYPTPasswordManager()

class BaseManager(object):
    def __init__(self, request):
        self.request = request
        self.session = get_session(request)

class UserManager(BaseManager):
    def get_all(self):
        return self.session.query(User).all()

    def get_by_email(self, email):
        return self.session.query(User).filter(User.email == email).first()

    def get_by_username(self, username):
        return self.session.query(User).filter(User.username == username).first()

    def get_by_username_or_email(self, username, email):
        return self.session.query(User).filter(
            or_(
                User.username == username,
                User.email == email
            )
        ).first()

    def get_by_email_password(self, email, password):
        user = self.get_by_email(email)

        if user:
            valid = self.validate_user(user, password)

            if valid:
                return user

    def get_by_activation(self, activation):
        user = self.session.query(User).filter(User.activation_pk == activation.pk).first()
        return user

    def get_by_pk(self, pk):
        """Gets an object by its primary key"""
        return self.session.query(User).filter(User.pk == pk).first()

    def get_user(self, username, password):
        user = self.get_by_username(username)

        valid = self.validate_user(user, password)

        if valid:
            return user

    def validate_user(self, user, password):
        if not user:
            return None

        if user.password == None:
            valid = False
        else:
            valid = crypt.check(user.password, password + user.salt)

        return valid


class UserGroupManager(BaseManager):
    def get_all(self):
        return self.session.query(UserGroup).all()

    def get_by_pk(self, pk):
        return self.session.query(UserGroup).filter(UserGroup.pk == pk).first()

class ActivationManager(BaseManager):
    def get_by_code(self, code):
        return self.session.query(Activation).filter(Activation.code == code).first()

    def get_all(self):
        return self.session.query(Activation).all()

class OrganizationManager(BaseManager):
    def get_by_pk(self, pk):
        return self.session.query(Organization).filter(Organization.pk == pk).first()

    def get_all(self):
        return self.session.query(Organization).all()
