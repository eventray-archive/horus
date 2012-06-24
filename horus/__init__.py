from pyramid.decorator  import reify
from pyramid.request    import Request
from pyramid.security   import unauthenticated_userid

from horus.schemas      import LoginSchema
from horus.schemas      import RegisterSchema
from horus.schemas      import ForgotPasswordSchema
from horus.schemas      import ResetPasswordSchema
from horus.schemas      import ProfileSchema
from horus.forms        import SubmitForm
from horus.resources    import RootFactory
from horus.interfaces   import IHorusUserClass
from horus.interfaces   import IHorusLoginForm
from horus.interfaces   import IHorusLoginSchema
from horus.interfaces   import IHorusRegisterForm
from horus.interfaces   import IHorusRegisterSchema
from horus.interfaces   import IHorusForgotPasswordForm
from horus.interfaces   import IHorusForgotPasswordSchema
from horus.interfaces   import IHorusResetPasswordForm
from horus.interfaces   import IHorusResetPasswordSchema
from horus.interfaces   import IHorusProfileForm
from horus.interfaces   import IHorusProfileSchema
from horus.routes       import build_routes

def groupfinder(userid, request):
    user = request.user
    groups = []

    if user:
        for group in user.groups:
            groups.append('group:%s' % group.name)

        groups.append('user:%s' % user.pk)

    return groups

def get_user(request):
    pk = unauthenticated_userid(request)
    user_class = request.registry.queryUtility(IHorusUserClass)

    if pk is not None:
        return user_class.get_by_pk(request, pk)

def get_class_from_config(settings, key):
    user_modules = settings.get(key).split('.')
    module = '.'.join(user_modules[:-1])
    klass = user_modules[-1]
    imported_module = __import__(module, fromlist=[klass])
    imported_class = getattr(imported_module, klass)

    return imported_class

def includeme(config):
    settings = config.registry.settings
    config.set_request_property(get_user, 'user', reify=True)

    config.set_root_factory(RootFactory)


    user_class = get_class_from_config(settings, 'horus.user_class')
    config.registry.registerUtility(user_class, IHorusUserClass)


    schemas = [
        (IHorusLoginSchema, LoginSchema),
        (IHorusRegisterSchema, RegisterSchema),
        (IHorusForgotPasswordSchema, ForgotPasswordSchema),
        (IHorusResetPasswordSchema, ResetPasswordSchema),
        (IHorusProfileSchema, ProfileSchema)
    ]

    forms = [
        IHorusLoginForm, IHorusRegisterForm, IHorusForgotPasswordForm,
        IHorusResetPasswordForm, IHorusProfileForm
    ]

    for iface, schema in schemas:
        if not config.registry.queryUtility(iface):
            config.registry.registerUtility(schema, iface)

    for form in forms:
        if not config.registry.queryUtility(form):
            config.registry.registerUtility(SubmitForm, form)

    config.include(build_routes)
    config.scan('horus')
