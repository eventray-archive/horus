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

    def test_json(self):
        model = TestModel()
        model.pk = 1
        model.start_date = datetime.now()

        assert model.__json__() == {'pk': 1, 'start_date': model.start_date.isoformat()}

class TestActivation(UnitTestBase):
    def test_create_activation_without_valid_until(self):
        from horus.tests.models import Activation

        activation1 = Activation()

        assert activation1.code != None
        assert activation1.valid_until > datetime.utcnow()

    def test_create_activation_with_valid_until(self):
        from horus.tests.models import Activation

        dt = datetime.utcnow()
        activation1 = Activation(valid_until=dt)

        assert activation1.code != None
        assert activation1.valid_until == dt

class TestUser(UnitTestBase):
    def test_password_hashing(self):
        from horus.tests.models import User
        user1 = User(user_name='sontek', email='sontek@gmail.com')
        user1.set_password('password')
        self.session.add(user1)
        self.session.flush()

        assert user1.password != 'password'
        assert user1.salt != None

    def test_acl(self):
        from horus.tests.models import User
        from pyramid.security import Allow

        user1 = User(user_name='sontek', email='sontek@gmail.com')
        user1.set_password('foo')

        self.session.add(user1)
        self.session.flush()

        assert user1.__acl__ == [(Allow, 'user:%s' % user1.pk, 'access_user')]


class TestGroup(UnitTestBase):
    def test_init(self):
        from horus.tests.models import Group
        group = Group(name='foo', description='bar')

        assert group.name == 'foo'
        assert group.description == 'bar'
