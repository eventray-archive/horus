import os

ROOT_PATH = os.path.dirname(__file__)

def pytest_sessionstart():
    from py.test import config

    # Only run database setup on master (in case of xdist/multiproc mode)
    if not hasattr(config, 'slaveinput'):
        from pyramid.config         import Configurator
        from horus.tests.models     import Base
        from paste.deploy.loadwsgi  import appconfig
        from sqlalchemy             import engine_from_config

        ROOT_PATH = os.path.dirname(__file__)
        settings = appconfig('config:' + os.path.join(ROOT_PATH, 'test.ini'))
        engine = engine_from_config(settings, prefix='sqlalchemy.')

        print 'Creating the tables on the test database %s' % engine

        config = Configurator(settings=settings)
        config.scan('horus.models')

        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)



