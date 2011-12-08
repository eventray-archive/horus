from pyramid import testing

from pyramid_signup.models import User
from pyramid_signup.tests import UnitTestBase

from mock import patch
from mock import Mock

class TestInitCase(UnitTestBase):
    def test_root_factory(self):
        from pyramid_signup import RootFactory
        from pyramid.security import Everyone
        from pyramid.security import Authenticated
        from pyramid.security import Allow
        from pyramid.security import ALL_PERMISSIONS

        root_factory = RootFactory(testing.DummyRequest())

        assert len(root_factory.__acl__) == 2

        for ace in root_factory.__acl__:
            assert ace[0] == Allow

            if ace[1] == 'group:admin':
                assert ace[2] == ALL_PERMISSIONS
            elif ace[1] == Authenticated:
                assert ace[2] == 'view'

    def test_request_factory(self):
        from pyramid_signup import SignUpRequestFactory
        user1 = User(username='sontek', first_name='john')
        self.session.add(user1)
        self.session.flush()

        with patch('pyramid_signup.unauthenticated_userid') as unauth:
            unauth.return_value = 1
            request = SignUpRequestFactory({})
            request.registry = Mock()

            getUtility = Mock()
            getUtility.return_value = self.session

            request.registry.getUtility = getUtility

            user = request.user

            assert user == user1
