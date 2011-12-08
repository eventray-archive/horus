import unittest
from sqlalchemy import engine_from_config
from pyramid import testing
from paste.deploy.loadwsgi import appconfig

from sqlalchemy.orm import sessionmaker

from mock import Mock

import os

from pyramid_signup.models import Entity
from pyramid_signup.interfaces import ISUSession

here = os.path.dirname(__file__)
settings = appconfig('config:' + os.path.join(here, '../../', 'test.ini'))

class BaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = engine_from_config(settings, prefix='sqlalchemy.')
        cls.Session = sessionmaker()


    def setUp(self):
        self.config = testing.setUp()

        connection = self.engine.connect()

        # begin a non-ORM transaction
        self.trans = connection.begin()

        # bind an individual Session to the connection
        self.session = self.Session(bind=connection)

        self.config.registry.registerUtility(self.session, ISUSession)

        Entity.metadata.bind=connection

    def tearDown(self):
        # rollback - everything that happened with the
        # Session above (including calls to commit())
        # is rolled back.
        testing.tearDown()
        self.trans.rollback()
        self.session.close()

class UnitTestBase(BaseTestCase):
    def setUp(self):
        self.config = testing.setUp(request=testing.DummyRequest())
        super(UnitTestBase, self).setUp()

    def get_csrf_request(self, post=None, request_method='GET'):
        csrf = 'abc'

        if not post:
            post = {}

        if not u'csrf_token' in post.keys():
            post.update({
                'csrf_token': csrf
            })

        request = testing.DummyRequest(post)

        request.session = Mock()
        csrf_token = Mock()
        csrf_token.return_value = csrf

        request.session.get_csrf_token = csrf_token
        request.method = request_method

        return request

