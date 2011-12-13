from pyramid.security import Authenticated
from pyramid.security import Allow
from pyramid.security import ALL_PERMISSIONS

from pyramid_signup.managers import OrganizationManager

class BaseFactory(object):
    def __init__(self, request):
        self.request = request
        self.is_root = False

class RootFactory(BaseFactory):
    @property
    def __acl__(self):
        defaultlist = [
            (Allow, 'group:admin', ALL_PERMISSIONS),
            (Allow, Authenticated, 'view'),
        ]

        return defaultlist

    def __init__(self, request):
        super(RootFactory, self).__init__(request)
        self.is_root = True

class OrganizationFactory(RootFactory):
    def __init__(self, request):
        self.request = request

    def __getitem__(self, key):
        mgr = OrganizationManager(self.request)

        org = mgr.get_by_pk(key)

        if org:
            org.__parent__ = self
            org.__name__ = key

        return org
