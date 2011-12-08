from pyramid_signup.tests import UnitTestBase
from pyramid import testing

from mock import Mock

class TestUserManager(UnitTestBase):
    def test_get_session(self):
        from pyramid_signup.interfaces import ISUSession
        from pyramid_signup.managers import UserManager

        request = testing.DummyRequest()
        request.registry = Mock()

        session = Mock()

        getUtility = Mock()
        getUtility.return_value = session

        request.registry.getUtility = getUtility

        mgr = UserManager(request)
        new_session = mgr.get_session()

        getUtility.assert_called_with(ISUSession)
        assert new_session == session


    def test_get_valid_user(self):
        from pyramid_signup.models import User
        from pyramid_signup.managers import UserManager

        user = User(username='sontek', password='temp')
        self.session.add(user)
        self.session.flush()

        request = testing.DummyRequest()
        mgr = UserManager(request)

        new_user = mgr.get_user('sontek', 'temp')

        assert user == new_user

    def test_get_invalid_user(self):
        from pyramid_signup.models import User
        from pyramid_signup.managers import UserManager

        user = User(username='sontek1', password='temp')
        self.session.add(user)
        self.session.flush()

        request = testing.DummyRequest()
        mgr = UserManager(request)

        new_user = mgr.get_user('sontek', 'temp')

        assert new_user == None

    def test_get_user_by_pk(self):
        from pyramid_signup.models import User
        from pyramid_signup.managers import UserManager

        user = User(username='sontek', password='temp')
        self.session.add(user)
        self.session.flush()

        request = testing.DummyRequest()
        mgr = UserManager(request)

        new_user = mgr.get_by_pk(user.pk)

        assert new_user == user

    def test_get_user_by_invalid_pk(self):
        from pyramid_signup.models import User
        from pyramid_signup.managers import UserManager

        user = User(username='sontek', password='temp')
        self.session.add(user)
        self.session.flush()

        request = testing.DummyRequest()
        mgr = UserManager(request)

        new_user = mgr.get_by_pk(2)

        assert new_user == None

    def test_get_user_by_username(self):
        from pyramid_signup.models import User
        from pyramid_signup.managers import UserManager

        user = User(username='sontek', password='temp')
        self.session.add(user)
        self.session.flush()

        request = testing.DummyRequest()
        mgr = UserManager(request)

        new_user = mgr.get_by_username('sontek')

        assert new_user == user

    def test_get_user_by_invalid_username(self):
        from pyramid_signup.models import User
        from pyramid_signup.managers import UserManager

        user = User(username='sontek', password='temp')
        self.session.add(user)
        self.session.flush()

        request = testing.DummyRequest()
        mgr = UserManager(request)

        new_user = mgr.get_by_username('sontek1')

        assert new_user == None
