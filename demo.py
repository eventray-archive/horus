from pyramid.config import Configurator
from pyramid.response import Response

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

def hello_world(request):
    return Response('Hello %(name)s!' % request.matchdict)

def main(global_config, **settings):
    config = Configurator()
    config.add_route('hello', '/hello/{name}')
    config.add_view(hello_world, route_name='hello')

    authn_policy = AuthTktAuthenticationPolicy('secret')
    config.set_authentication_policy(authn_policy)

    authz_policy = ACLAuthorizationPolicy()
    config.set_authorization_policy(authz_policy)

    app = config.make_wsgi_app()

    return app
