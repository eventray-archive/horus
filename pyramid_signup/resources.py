from pyramid.security import Authenticated
from pyramid.security import Allow
from pyramid.security import ALL_PERMISSIONS

from pyramid_signup.models import Organization

class RootFactory(object):
    @property
    def __acl__(self):
        defaultlist = [
            (Allow, 'group:admin', ALL_PERMISSIONS),
            (Allow, Authenticated, 'view'),
        ]

        return defaultlist

    def __init__(self, request):
        pass  # pragma: no cover

class OrganizationFactory(RootFactory):
    def __init__(self, request):
        self.request = request

    def __getitem__(self, key):
        account = Organization.get_by_pk(key)

        if account:
            account.__parent__ = self
            account.__name__ = key

        return account
