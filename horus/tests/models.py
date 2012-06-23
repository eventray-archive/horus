from sqlalchemy.ext.declarative import declarative_base
from horus.models               import BaseModel
from horus.models               import UserMixin
from horus.models               import UserGroupMixin
from horus.models               import OrganizationMixin

Base = declarative_base(cls=BaseModel)

class User(Base, UserMixin):
    pass

class UserGroup(Base, UserGroupMixin):
    pass

class Organization(Base, OrganizationMixin):
    pass

