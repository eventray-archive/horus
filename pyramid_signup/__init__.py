from pyramid.decorator import reify
from pyramid.request import Request
from pyramid.security import unauthenticated_userid

from pyramid_signup.managers import UserManager
from pyramid_signup.schemas import LoginSchema
from pyramid_signup.schemas import RegisterSchema
from pyramid_signup.schemas import ForgotPasswordSchema
from pyramid_signup.schemas import ResetPasswordSchema
from pyramid_signup.schemas import ProfileSchema
from pyramid_signup.forms import SubmitForm
from pyramid_signup.resources import RootFactory
from pyramid_signup.interfaces import ISULoginForm
from pyramid_signup.interfaces import ISULoginSchema
from pyramid_signup.interfaces import ISURegisterForm
from pyramid_signup.interfaces import ISURegisterSchema
from pyramid_signup.interfaces import ISUForgotPasswordForm
from pyramid_signup.interfaces import ISUForgotPasswordSchema
from pyramid_signup.interfaces import ISUResetPasswordForm
from pyramid_signup.interfaces import ISUResetPasswordSchema
from pyramid_signup.interfaces import ISUProfileForm
from pyramid_signup.interfaces import ISUProfileSchema

from pyramid_signup.routes import build_routes

def groupfinder(userid, request):
    user = request.user
    groups = []

    if user:
        for org in user.organizations:
            groups.append('organization:%s' % org.pk)

        for group in user.groups:
            groups.append('group:%s' % group.name)

        groups.append('user:%s' % user.pk)

#        if user.kind == 'admin':
#            groups.append('group:admin')

#        account_perms = session.query(AccountUserPermission) \
#                .filter(AccountUserPermission.user_pk == user.pk).all()
#
#        for account_perm in account_perms:
#            if account_perm.has_access:
#                groups.append('account:%s:%s' % (account_perm.account_pk, account_perm.key))
#
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
    config.scan('pyramid_signup')
