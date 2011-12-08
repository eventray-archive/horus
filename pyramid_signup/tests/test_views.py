from pyramid import testing

from mock import Mock
from mock import patch

import os

from pyramid_signup.tests import UnitTestBase
from pyramid_signup.models import User

here = os.path.dirname(__file__)

class TestAuthViews(UnitTestBase):
    def test_auth_controller_extensions(self):
        from pyramid_signup.views import AuthController
        from pyramid_signup.interfaces import ISULoginSchema
        from pyramid_signup.interfaces import ISULoginForm

        self.config.add_route('index', '/')

        request = testing.DummyRequest()

        getUtility = Mock()
        getUtility.return_value = True

        schema = Mock()
        form = Mock()

        self.config.registry.registerUtility(schema, ISULoginSchema)
        self.config.registry.registerUtility(form, ISULoginForm)

        AuthController(request)

        assert schema.is_called
        assert schema.bind.is_called
        assert form.is_called


    def test_login_loads(self):
        from pyramid_signup.views import AuthController
        self.config.add_route('index', '/')
        self.config.include('pyramid_signup')

        request = testing.DummyRequest()
        request.user = None
        view = AuthController(request)
        response = view.get()

        assert response.get('form', None)

    def test_login_redirects_if_logged_in(self):
        from pyramid_signup.views import AuthController
        self.config.add_route('index', '/')
        self.config.include('pyramid_signup')

        request = testing.DummyRequest()
        request.user = Mock()
        view = AuthController(request)

        response = view.get()
        assert response.status_int == 302

    def test_login_fails_empty(self):
        """ Make sure we can't login with empty credentials"""
        from pyramid_signup.views import AuthController
        self.config.add_route('index', '/')
        self.config.include('pyramid_signup')

        request = testing.DummyRequest(post={
            'submit': True,
        })

        view = AuthController(request)
        response = view.post()
        errors = response['errors']

        assert errors[0].node.name == u'csrf_token'
        assert errors[0].msg == u'Required'
        assert errors[1].node.name == u'Username'
        assert errors[1].msg == u'Required'
        assert errors[2].node.name == u'Password'
        assert errors[2].msg == u'Required'

    def test_csrf_invalid_fails(self):
        """ Make sure we can't login with a bad csrf """
        from pyramid_signup.views import AuthController
        self.config.add_route('index', '/')
        self.config.include('pyramid_signup')

        request = self.get_csrf_request(post={
                    'submit': True,
                    'login': 'admin',
                    'password': 'test123',
                    'csrf_token': 'abc2'
                })

        view = AuthController(request)
        response = view.post()

        errors = response['errors']

        assert errors[0].node.name == u'csrf_token'
        assert errors[0].msg == u'Invalid cross-site scripting token'


    def test_login_fails_bad_credentials(self):
        """ Make sure we can't login with bad credentials"""
        from pyramid_signup.views import AuthController
        self.config.add_route('index', '/')
        self.config.include('pyramid_signup')

        request = self.get_csrf_request(post={
                'submit': True,
                'Username': 'admin',
                'Password': 'test123',
            })

        flash = Mock()
        request.session.flash = flash

        view = AuthController(request)
        view.post()

        flash.assert_called_with(u'Invalid username or password.', 'error')

    def test_login_succeeds(self):
        """ Make sure we can login """
        admin = User(username='sontek', password='temp')
        admin.activated = True

        self.session.add(admin)
        self.session.flush()

        from pyramid_signup.views import AuthController
        self.config.add_route('index', '/')

        self.config.include('pyramid_signup')

        request = self.get_csrf_request(post={
                'submit': True,
                'Username': 'sontek',
                'Password': 'temp',
            })

        view = AuthController(request)
        response = view.post()

        assert response.status_int == 302

    def test_inactive_login_fails(self):
        """ Make sure we can't login with an inactive user """
        user = User(username='sontek', password='temp')

        self.session.add(user)
        self.session.flush()

        from pyramid_signup.views import AuthController
        self.config.add_route('index', '/')
        self.config.include('pyramid_signup')

        request = self.get_csrf_request(post={
                'submit': True,
                'Username': 'sontek',
                'Password': 'temp',
            })

        flash = Mock()

        request.session.flash = flash

        view = AuthController(request)
        view.post()

        flash.assert_called_with(u'Your account is not active, please check your e-mail.',
            'error')

    def test_logout(self):
        from pyramid_signup.views import AuthController
        self.config.add_route('index', '/')
        self.config.include('pyramid_signup')
        request = testing.DummyRequest()

        flash = Mock()
        invalidate = Mock()

        request.user = Mock()
        request.session = Mock()
        request.session.invalidate = invalidate
        request.session.flash = flash

        view = AuthController(request)
        with patch('pyramid_signup.views.forget') as forget:
            with patch('pyramid_signup.views.HTTPFound') as HTTPFound:
                view.logout()
                flash.assert_called_with(u'Logged out successfully.', 'success')
                forget.assert_called_with(request)
                assert invalidate.called
                assert HTTPFound.called
