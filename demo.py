from pyramid.config import Configurator

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

def main(global_config, **settings):
    config = Configurator()
    config.include('pyramid_signup')

    authn_policy = AuthTktAuthenticationPolicy('secret')
    config.set_authentication_policy(authn_policy)

    authz_policy = ACLAuthorizationPolicy()
    config.set_authorization_policy(authz_policy)

    app = config.make_wsgi_app()

    return app
