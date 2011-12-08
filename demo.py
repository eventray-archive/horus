from pyramid.config import Configurator
from pyramid.response import Response

from pyramid_beaker import session_factory_from_settings

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import engine_from_config

from zope.sqlalchemy import ZopeTransactionExtension

from pyramid_signup.interfaces import ISUSession

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

def index(request):
    return Response('Index!' % request.matchdict)

def main(global_config, **settings):
    config = Configurator()

    config.add_route('index', '/')
    config.add_view(index, route_name='index')

    authn_policy = AuthTktAuthenticationPolicy('secret')
    config.set_authentication_policy(authn_policy)

    authz_policy = ACLAuthorizationPolicy()
    config.set_authorization_policy(authz_policy)

    session_factory = session_factory_from_settings(settings)

    config.set_session_factory(session_factory)


    engine = engine_from_config(settings, prefix='sqlalchemy.')
    DBSession.configure(bind=engine)
    
    config.registry.registerUtility(DBSession, ISUSession)

    config.include('pyramid_signup')


    app = config.make_wsgi_app()

    return app
