from pyramid_signup.tests import UnitTestBase
from pyramid import testing

class TestUserManager(UnitTestBase):
    def test_get_valid_user(self):
        from pyramid_signup.models import User
        from pyramid_signup.managers import UserManager

        user = User(username='sontek', password='temp')
        self.session.add(user)
        self.session.commit()

        request = testing.DummyRequest()
        mgr = UserManager(request)

        new_user = mgr.get_user('sontek', 'temp')

        assert user == new_user

    def test_get_invalid_user(self):
        from pyramid_signup.models import User
        from pyramid_signup.managers import UserManager

        user = User(username='sontek1', password='temp')
        self.session.add(user)
        self.session.commit()

        request = testing.DummyRequest()
        mgr = UserManager(request)

        new_user = mgr.get_user('sontek', 'temp')

        assert new_user == None

    def test_get_user_by_pk(self):
        from pyramid_signup.models import User
        from pyramid_signup.managers import UserManager

        user = User(username='sontek', password='temp')
        self.session.add(user)
        self.session.commit()

        request = testing.DummyRequest()
        mgr = UserManager(request)

        new_user = mgr.get_by_pk(user.pk)

        assert new_user == user

    def test_get_user_by_invalid_pk(self):
        from pyramid_signup.models import User
        from pyramid_signup.managers import UserManager

        user = User(username='sontek', password='temp')
        self.session.add(user)
        self.session.commit()

        request = testing.DummyRequest()
        mgr = UserManager(request)

        new_user = mgr.get_by_pk(2)

        assert new_user == None

    def test_get_user_by_username(self):
        from pyramid_signup.models import User
        from pyramid_signup.managers import UserManager

        user = User(username='sontek', password='temp')
        self.session.add(user)
        self.session.commit()

        request = testing.DummyRequest()
        mgr = UserManager(request)

        new_user = mgr.get_by_username('sontek')

        assert new_user == user

    def test_get_user_by_invalid_username(self):
        from pyramid_signup.models import User
        from pyramid_signup.managers import UserManager

        user = User(username='sontek', password='temp')
        self.session.add(user)
        self.session.commit()

        request = testing.DummyRequest()
        mgr = UserManager(request)

        new_user = mgr.get_by_username('sontek1')

        assert new_user == None

    def test_get_user_by_email(self):
        from pyramid_signup.models import User
        from pyramid_signup.managers import UserManager

        user = User(username='sontek', password='temp', email='sontek@gmail.com')
        self.session.add(user)
        self.session.commit()

        request = testing.DummyRequest()
        mgr = UserManager(request)

        new_user = mgr.get_by_email(user.email)

        assert new_user == user

    def test_get_user_by_invalid_email(self):
        from pyramid_signup.models import User
        from pyramid_signup.managers import UserManager

        user = User(username='sontek', password='temp', email='sontek@gmail.com')
        self.session.add(user)
        self.session.commit()

        request = testing.DummyRequest()
        mgr = UserManager(request)

        new_user = mgr.get_by_email('sontek1@gmail.com')

        assert new_user == None

    def test_get_user_by_activation(self):
        from pyramid_signup.models import User
        from pyramid_signup.models import Activation
        from pyramid_signup.managers import UserManager

        user = User(username='sontek', password='temp', email='sontek@gmail.com')
        activation = Activation()
        user.activation = activation

        self.session.add(user)
        self.session.commit()

        request = testing.DummyRequest()
        mgr = UserManager(request)

        new_user = mgr.get_by_activation(activation)

        assert new_user == user
