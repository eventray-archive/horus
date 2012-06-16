from pyramid.decorator import reify
from pyramid.request import Request
from pyramid.security import unauthenticated_userid

from horus.managers import UserManager
from horus.schemas import LoginSchema
from horus.schemas import RegisterSchema
from horus.schemas import ForgotPasswordSchema
from horus.schemas import ResetPasswordSchema
from horus.schemas import ProfileSchema
from horus.forms import SubmitForm
from horus.resources import RootFactory
from horus.interfaces import ISULoginForm
from horus.interfaces import ISULoginSchema
from horus.interfaces import ISURegisterForm
from horus.interfaces import ISURegisterSchema
from horus.interfaces import ISUForgotPasswordForm
from horus.interfaces import ISUForgotPasswordSchema
from horus.interfaces import ISUResetPasswordForm
from horus.interfaces import ISUResetPasswordSchema
from horus.interfaces import ISUProfileForm
from horus.interfaces import ISUProfileSchema

from horus.routes import build_routes

def groupfinder(userid, request):
    user = request.user
    groups = []

    if user:
        for org in user.organizations:
            groups.append('organization:%s' % org.pk)

        for group in user.groups:
            groups.append('group:%s' % group.name)

        groups.append('user:%s' % user.pk)

    return groups

class SignUpRequestFactory(Request):
    @reify
    def user(self):
        pk = unauthenticated_userid(self)

        if pk is not None:
            mgr = UserManager(self)
            return mgr.get_by_pk(pk)


def includeme(config):
    config.set_root_factory(RootFactory)

    config.set_request_factory(SignUpRequestFactory)

    schemas = [
        (ISULoginSchema, LoginSchema),
        (ISURegisterSchema, RegisterSchema),
        (ISUForgotPasswordSchema, ForgotPasswordSchema),
        (ISUResetPasswordSchema, ResetPasswordSchema),
        (ISUProfileSchema, ProfileSchema)
    ]

    forms = [
        ISULoginForm, ISURegisterForm, ISUForgotPasswordForm,
        ISUResetPasswordForm, ISUProfileForm
    ]

    for iface, schema in schemas:
        if not config.registry.queryUtility(iface):
            config.registry.registerUtility(schema, iface)

    for form in forms:
        if not config.registry.queryUtility(form):
            config.registry.registerUtility(SubmitForm, form)

    config.include(build_routes)
    config.scan('horus')
