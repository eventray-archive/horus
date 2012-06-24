from horus.tests import UnitTestBase
from pyramid import testing

from mock import Mock

class TestLib(UnitTestBase):
    def test_get_session(self):
        from horus.interfaces import IHorusSession
        from horus.lib import get_session
        request = testing.DummyRequest()
        request.registry = Mock()

        session = Mock()

        getUtility = Mock()
        getUtility.return_value = session

        request.registry.getUtility = getUtility

        new_session = get_session(request)

        getUtility.assert_called_with(IHorusSession)
        assert new_session == session


