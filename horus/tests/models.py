from sqlalchemy.ext.declarative import declarative_base
from horus.models               import BaseModel
from horus.models               import GroupMixin
from horus.models               import UserMixin
from horus.models               import UserGroupMixin
from horus.models               import OrganizationMixin

Base = declarative_base(cls=BaseModel)

class Group(GroupMixin, Base):
    pass

class User(UserMixin, Base):
    pass

class UserGroup(UserGroupMixin, Base):
    pass

class Organization(OrganizationMixin, Base):
    pass

