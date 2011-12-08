from pyramid_signup.interfaces import ISULoginForm
from pyramid_signup.interfaces import ISULoginSchema
from pyramid_signup.schemas import LoginSchema
from deform import Form

def includeme(config):
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')

    if not config.registry.queryUtility(ISULoginSchema):
        config.registry.registerUtility(LoginSchema, ISULoginSchema)

    if not config.registry.queryUtility(ISULoginForm):
        config.registry.registerUtility(Form, ISULoginForm)

    config.scan('pyramid_signup')
