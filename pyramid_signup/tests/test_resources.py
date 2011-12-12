from pyramid import testing

from pyramid_signup.tests import UnitTestBase

class TestResources(UnitTestBase):
    def test_organization_factory(self):
        from pyramid_signup.resources import OrganizationFactory
        from pyramid_signup.models import Organization
        from pyramid_signup.models import User

        user = User(username='sontek', password='temp')
        self.session.add(user)

        organization = Organization('test org', user)
        self.session.add(organization)
        self.session.commit()

        request = testing.DummyRequest()
        factory = OrganizationFactory(request)

        org = factory[1]

        assert factory.request == request
        assert org == organization
