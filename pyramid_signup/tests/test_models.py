from pyramid_signup.tests import UnitTestBase
from pyramid_signup.models import SUEntity
from sqlalchemy.types import DateTime

from sqlalchemy import Column

from datetime import datetime

class TestModel(SUEntity):
    start_date = Column(DateTime)

class TestModels(UnitTestBase):
    def test_tablename(self):
        model = TestModel()
        assert model.__tablename__ == 'test_model'

    def test_serialize(self):
        model = TestModel()
        model.pk = 1
        model.start_date = datetime.now()

        assert model.serialize() == {'pk': 1, 'start_date': model.start_date.isoformat()}

class TestActivation(UnitTestBase):
    def test_create_activation_without_valid_until(self):
        from pyramid_signup.models import Activation

        activation1 = Activation()

        assert activation1.code != None
        assert activation1.valid_until > datetime.utcnow()

    def test_create_activation_with_valid_until(self):
        from pyramid_signup.models import Activation

        dt = datetime.utcnow()
        activation1 = Activation(valid_until=dt)

        assert activation1.code != None
        assert activation1.valid_until == dt

class TestOrganizations(UnitTestBase):
    def test_create_organization(self):
        from pyramid_signup.models import Organization
        from pyramid_signup.models import User

        owner = User()
        self.session.add(owner)
        self.session.flush()

        organization = Organization('foo', owner)
        self.session.add(organization)
        self.session.flush()

        assert organization.name == 'foo'
        assert organization.create_date != None

    def test_organization_acl(self):
        from pyramid_signup.models import Organization
        from pyramid_signup.models import User
        from pyramid.security import Allow

        owner = User()
        self.session.add(owner)
        self.session.flush()

        organization = Organization('foo', owner)
        self.session.add(organization)
        self.session.flush()

        ace =  organization.__acl__

        assert len(ace) == 1
        assert ace[0][0] == Allow
        assert ace[0][1] == 'organization:1'
        assert ace[0][2] == 'access_organization'


class TestUser(UnitTestBase):
    def test_password_hashing(self):
        from pyramid_signup.models import User
        user1 = User(username='sontek', first_name='john',
                last_name='anderson', password='password')

        self.session.add(user1)
        self.session.flush()

        assert user1.password != 'password'
        assert user1.salt != None

    def test_display_name_full(self):
        from pyramid_signup.models import User
        user1 = User(username='sontek', first_name='john',
                last_name='anderson', password='password')

        self.session.add(user1)
        self.session.flush()

        assert user1.display_name == 'john anderson'

    def test_display_name_only_username(self):
        from pyramid_signup.models import User
        user1 = User(username='sontek')


        self.session.add(user1)
        self.session.flush()

        assert user1.display_name == 'sontek'


