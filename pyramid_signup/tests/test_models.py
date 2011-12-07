from pyramid_signup.tests import UnitTestBase
from pyramid_signup.models import Entity
from sqlalchemy.types import DateTime

from sqlalchemy import Column

from datetime import datetime

class TestModel(Entity):
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

#class TestOrganizations(UnitTestBase):
#    def test_login_loads(self):
#
#        assert 
