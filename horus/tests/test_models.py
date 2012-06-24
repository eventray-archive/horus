from horus.tests import UnitTestBase
from horus.tests.models import Base
from sqlalchemy.types import DateTime

from sqlalchemy import Column

from datetime import datetime

class TestModel(Base):
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
        from horus.models import Activation

        activation1 = Activation()

        assert activation1.code != None
        assert activation1.valid_until > datetime.utcnow()

    def test_create_activation_with_valid_until(self):
        from horus.models import Activation

        dt = datetime.utcnow()
        activation1 = Activation(valid_until=dt)

        assert activation1.code != None
        assert activation1.valid_until == dt

class TestOrganizations(UnitTestBase):
    def test_create_organization(self):
        from horus.models import Organization
        from horus.models import User

        owner = User()
        self.session.add(owner)
        self.session.flush()

        organization = Organization('foo', owner)
        self.session.add(organization)
        self.session.flush()

        assert organization.name == 'foo'
        assert organization.create_date != None

    def test_organization_acl(self):
        from horus.models import Organization
        from horus.models import User
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
        from horus.models import User
        user1 = User(username='sontek', first_name='john',
                last_name='anderson', password='password')

        self.session.add(user1)
        self.session.flush()

        assert user1.password != 'password'
        assert user1.salt != None

    def test_display_name_full(self):
        from horus.models import User
        user1 = User(username='sontek', first_name='john',
                last_name='anderson', password='password')

        self.session.add(user1)
        self.session.flush()

        assert user1.display_name == 'john anderson'

    def test_display_name_only_username(self):
        from horus.models import User
        user1 = User(username='sontek')


        self.session.add(user1)
        self.session.flush()

        assert user1.display_name == 'sontek'

    def test_acl(self):
        from horus.models import User
        from pyramid.security import Allow

        user1 = User(username='sontek')


        self.session.add(user1)
        self.session.flush()

        assert user1.__acl__ == [(Allow, 'user:1', 'access_user')]


class TestUserGroup(UnitTestBase):
    def test_init(self):
        from horus.models import UserGroup
        group = UserGroup('foo', 'bar')

        assert group.name == 'foo'
        assert group.description == 'bar'
