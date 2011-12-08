from pyramid.security import Everyone
from pyramid.security import Authenticated
from pyramid.security import Allow
from pyramid.security import ALL_PERMISSIONS
from pyramid_signup.interfaces import ISULoginForm
from pyramid_signup.interfaces import ISULoginSchema
from pyramid_signup.schemas import LoginSchema
from pyramid.decorator import reify
from pyramid.request import Request
from pyramid.security import unauthenticated_userid

from deform import Form

from pyramid_signup.managers import UserManager

class RootFactory(object):
    @property
    def __acl__(self):
        defaultlist = [
            (Allow, 'group:admin', ALL_PERMISSIONS),
            (Allow, Everyone, 'view'),
            (Allow, Authenticated, 'authed'),
        ]

        return defaultlist

    def __init__(self, request):
        pass  # pragma: no cover

class SignUpRequestFactory(Request):
    @reify
    def user(self):
        pk = unauthenticated_userid(self)

        if pk is not None:
            mgr = UserManager(self)
            return mgr.get_by_pk(pk)



def includeme(config):
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')

    config.set_root_factory(RootFactory)

    config.set_request_factory(SignUpRequestFactory)

    if not config.registry.queryUtility(ISULoginSchema):
        config.registry.registerUtility(LoginSchema, ISULoginSchema)

    if not config.registry.queryUtility(ISULoginForm):
        config.registry.registerUtility(Form, ISULoginForm)

    config.scan('pyramid_signup')
