from horus.tests import UnitTestBase
from pyramid import testing

class TestUserManager(UnitTestBase):
    def test_get_valid_user(self):
        from horus.models import User
        from horus.managers import UserManager

        user = User(username='sontek', password='temp')
        self.session.add(user)
        self.session.commit()

        request = testing.DummyRequest()
        mgr = UserManager(request)

        new_user = mgr.get_user('sontek', 'temp')

        assert user == new_user

    def test_get_all_users(self):
        from horus.models import User
        from horus.managers import UserManager

        user = User(username='sontek', password='temp')
        user2 = User(username='sontek2', password='temp')
        self.session.add(user)
        self.session.add(user2)
        self.session.commit()

        request = testing.DummyRequest()
        mgr = UserManager(request)

        users = mgr.get_all()

        assert len(users) == 2

    def test_get_invalid_user(self):
        from horus.models import User
        from horus.managers import UserManager

        user = User(username='sontek1', password='temp')
        self.session.add(user)
        self.session.commit()

        request = testing.DummyRequest()
        mgr = UserManager(request)

        new_user = mgr.get_user('sontek', 'temp')

        assert new_user == None

    def test_get_user_by_pk(self):
        from horus.models import User
        from horus.managers import UserManager

        user = User(username='sontek', password='temp')
        self.session.add(user)
        self.session.commit()

        request = testing.DummyRequest()
        mgr = UserManager(request)

        new_user = mgr.get_by_pk(user.pk)

        assert new_user == user

    def test_get_user_by_invalid_pk(self):
        from horus.models import User
        from horus.managers import UserManager

        user = User(username='sontek', password='temp')
        self.session.add(user)
        self.session.commit()

        request = testing.DummyRequest()
        mgr = UserManager(request)

        new_user = mgr.get_by_pk(2)

        assert new_user == None

    def test_get_user_by_username(self):
        from horus.models import User
        from horus.managers import UserManager

        user = User(username='sontek', password='temp')
        self.session.add(user)
        self.session.commit()

        request = testing.DummyRequest()
        mgr = UserManager(request)

        new_user = mgr.get_by_username('sontek')

        assert new_user == user

    def test_get_user_by_invalid_username(self):
        from horus.models import User
        from horus.managers import UserManager

        user = User(username='sontek', password='temp')
        self.session.add(user)
        self.session.commit()

        request = testing.DummyRequest()
        mgr = UserManager(request)

        new_user = mgr.get_by_username('sontek1')

        assert new_user == None

    def test_get_user_by_email(self):
        from horus.models import User
        from horus.managers import UserManager

        user = User(username='sontek', password='temp', email='sontek@gmail.com')
        self.session.add(user)
        self.session.commit()

        request = testing.DummyRequest()
        mgr = UserManager(request)

        new_user = mgr.get_by_email(user.email)

        assert new_user == user

    def test_get_user_by_invalid_email(self):
        from horus.models import User
        from horus.managers import UserManager

        user = User(username='sontek', password='temp', email='sontek@gmail.com')
        self.session.add(user)
        self.session.commit()

        request = testing.DummyRequest()
        mgr = UserManager(request)

        new_user = mgr.get_by_email('sontek1@gmail.com')

        assert new_user == None

    def test_get_user_by_activation(self):
        from horus.models import User
        from horus.models import Activation
        from horus.managers import UserManager

        user = User(username='sontek', password='temp', email='sontek@gmail.com')
        activation = Activation()
        user.activation = activation

        self.session.add(user)
        self.session.commit()

        request = testing.DummyRequest()
        mgr = UserManager(request)

        new_user = mgr.get_by_activation(activation)

        assert new_user == user

    def test_get_user_by_activation_with_multiple_users(self):
        from horus.models import User
        from horus.models import Activation
        from horus.managers import UserManager

        user1 = User(username='sontek1', password='temp', email='sontek@gmail.com')
        user2 = User(username='sontek2', password='temp', email='sontek@gmail.com')

        activation = Activation()
        user2.activation = activation

        self.session.add(user1)
        self.session.add(user2)

        self.session.commit()

        request = testing.DummyRequest()
        mgr = UserManager(request)

        new_user = mgr.get_by_activation(activation)

        assert new_user == user2

class TestActivationManager(UnitTestBase):
    def test_get_activation(self):
        from horus.models import Activation
        from horus.managers import ActivationManager

        activation = Activation()
        self.session.add(activation)
        self.session.commit()

        request = testing.DummyRequest()
        mgr = ActivationManager(request)

        new_activation = mgr.get_by_code(activation.code)

        assert activation == new_activation

    def test_get_user_activation(self):
        from horus.models import Activation
        from horus.managers import ActivationManager
        from horus.managers import UserManager
        from horus.models import User

        user1 = User(username='sontek1', password='temp', email='sontek@gmail.com')
        user2 = User(username='sontek2', password='temp', email='sontek@gmail.com')

        activation = Activation()
        user2.activation = activation

        self.session.add(user1)
        self.session.add(user2)
        self.session.commit()

        request = testing.DummyRequest()
        mgr = ActivationManager(request)
        user_mgr = UserManager(request)

        new_user = user_mgr.get_by_username('sontek2')

        new_activation = mgr.get_by_code(activation.code)

        assert activation == new_activation
        assert new_user.activation == new_activation

class TestOrganizationManager(UnitTestBase):
    def test_get_organization(self):
        from horus.models import Organization
        from horus.models import User
        from horus.managers import OrganizationManager

        user = User(username='sontek', password='temp')
        self.session.add(user)

        organization = Organization('test org', user)
        self.session.add(organization)
        self.session.commit()

        request = testing.DummyRequest()
        mgr = OrganizationManager(request)

        new_org = mgr.get_by_pk(organization.pk)

        assert organization == new_org

    def test_get_organization_bad_pk(self):
        from horus.models import Organization
        from horus.models import User
        from horus.managers import OrganizationManager

        user = User(username='sontek', password='temp')
        self.session.add(user)

        organization = Organization('test org', user)
        self.session.add(organization)
        self.session.commit()

        request = testing.DummyRequest()
        mgr = OrganizationManager(request)

        new_org = mgr.get_by_pk(99999)

        assert new_org == None

    def test_get_organization_get_all(self):
        from horus.models import Organization
        from horus.models import User
        from horus.managers import OrganizationManager

        user = User(username='sontek', password='temp')
        self.session.add(user)

        organization = Organization('test org', user)
        self.session.add(organization)
        self.session.commit()

        request = testing.DummyRequest()
        mgr = OrganizationManager(request)

        orgs = mgr.get_all()

        assert len(orgs) == 1

class TestUserGroupManager(UnitTestBase):
    def test_get_all(self):
        from horus.models import UserGroup
        from horus.models import User
        from horus.managers import UserGroupManager

        user = User(username='sontek', password='temp')
        self.session.add(user)

        group = UserGroup('admin', 'group for admins')
        group.users.append(user)
        self.session.add(group)
        self.session.commit()

        request = testing.DummyRequest()
        mgr = UserGroupManager(request)

        groups = mgr.get_all()

        assert len(groups) == 1

    def test_get_by_pk(self):
        from horus.models import UserGroup
        from horus.models import User
        from horus.managers import UserGroupManager

        group = UserGroup('admin', 'group for admins')
        group2 = UserGroup('employees', 'group for employees')

        self.session.add(group)
        self.session.add(group2)

        self.session.commit()

        request = testing.DummyRequest()
        mgr = UserGroupManager(request)

        group = mgr.get_by_pk(2)

        assert group.name == 'employees'




