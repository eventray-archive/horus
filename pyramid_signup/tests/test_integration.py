from pyramid_signup.tests import IntegrationTestBase
from pyramid import testing
from mock import patch
from mock import Mock

class TestViews(IntegrationTestBase):
    def test_index(self):
        """ Call the index view, make sure routes are working """
        res = self.app.get('/')
        assert res.status_int == 200

    def test_get_register(self):
        """ Call the register view, make sure routes are working """
        res = self.app.get('/register')
        assert res.status_int == 200

    def test_get_login(self):
        """ Call the login view, make sure routes are working """
        res = self.app.get('/login')
        self.assertEqual(res.status_int, 200)

    def test_login_redirects_if_logged_in(self):
        request = testing.DummyRequest()
        from pyramid_signup.views import AuthController
        with patch.object(AuthController, 'request', request) as request:
            request.user = Mock()
            res = self.app.get('/login').follow()
            #TODO: Patch index request as well so that it redirects to dashboard
            assert 'index' in res.body

    def test_empty_login(self):
        """ Empty login fails """
        res = self.app.post('/login', {'submit': True})

        assert "There was a problem with your submission" in res.body
        assert "Required" in res.body
        assert res.status_int == 200

    def test_valid_login(self):
        """ Call the login view, make sure routes are working """
        from pyramid_signup.models import User
        admin = User(username='sontek', password='temp')
        admin.activated = True
        self.session.add(admin)
        self.session.flush()

        res = self.app.get('/login')

        csrf = res.form.fields['csrf_token'][0].value

        res = self.app.post('/login', 
            {
                'submit': True,
                'Username': 'sontek',
                'Password': 'temp',
                'csrf_token': csrf
            }
        )

        assert res.status_int == 302

    def test_inactive_login(self):
        """ Make sure inactive users can't sign in"""
        from pyramid_signup.models import User
        admin = User(username='sontek', password='temp')
        self.session.add(admin)
        self.session.flush()

        res = self.app.get('/login')

        csrf = res.form.fields['csrf_token'][0].value

        res = self.app.post('/login', 
            {
                'submit': True,
                'Username': 'sontek',
                'Password': 'temp',
                'csrf_token': csrf
            }
        )

        assert 'Your account is not active, please check your e-mail.' in res.body
