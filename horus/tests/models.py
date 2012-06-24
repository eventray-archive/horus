from sqlalchemy.ext.declarative import declarative_base
from horus.models               import GroupMixin
from horus.models               import UserMixin
from horus.models               import UserGroupMixin

Base = declarative_base()

class User(UserMixin, Base):
    pass

class Group(GroupMixin, Base):
    pass

class UserGroup(UserGroupMixin, Base):
    pass
