from pyramid import testing
from pyramid_signup.tests import UnitTestBase

from mock import patch
from mock import Mock

class TestInitCase(UnitTestBase):
    def test_root_factory(self):
        from pyramid_signup import RootFactory
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
        from pyramid_signup.models import User
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

    def test_group_finder(self):
        from pyramid_signup import groupfinder
        from pyramid_signup.models import User
        from pyramid_signup.models import UserGroup
        from pyramid_signup.models import Organization
        
        group = UserGroup('foo', 'bar')
        user1 = User(username='sontek', first_name='john')
        organization = Organization('foo', user1)
        group.users.append(user1)

        self.session.add(organization)
        self.session.add(group)
        self.session.add(user1)
        self.session.flush()

        request = Mock()
        request.user = user1

        results = groupfinder(1, request)

        assert 'organization:1' in results
        assert 'group:foo' in results
        assert 'user:%s' % (user1.pk) in results
        assert len(results) == 3

    def test_group_finder_no_groups(self):
        from pyramid_signup import groupfinder
        from pyramid_signup.models import User
        from pyramid_signup.models import UserGroup
        from pyramid_signup.models import Organization
        
        group = UserGroup('foo', 'bar')
        user1 = User(username='sontek', first_name='john')
        user2 = User(username='sontek2', first_name='john')
        organization = Organization('foo', user1)
        group.users.append(user1)

        self.session.add(organization)
        self.session.add(group)
        self.session.add(user1)
        self.session.add(user2)
        self.session.flush()

        request = Mock()
        request.user = user2

        results = groupfinder(2, request)

        assert len(results) == 1
        assert 'user:%s' % (user2.pk) in results
