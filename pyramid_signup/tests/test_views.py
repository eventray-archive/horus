from pyramid import testing

from mock import Mock
from mock import patch

from pyramid_signup.tests import UnitTestBase

class TestAuthController(UnitTestBase):
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

        assert schema.called
        assert form.called


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
        }, request_method='POST')

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
                }, request_method='POST')

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
            }, request_method='POST')

        flash = Mock()
        request.session.flash = flash

        view = AuthController(request)
        view.post()

        flash.assert_called_with(u'Invalid username or password.', 'error')

    def test_login_succeeds(self):
        """ Make sure we can login """
        from pyramid_signup.models import User
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
            }, request_method='POST')

        view = AuthController(request)
        response = view.post()

        assert response.status_int == 302

    def test_inactive_login_fails(self):
        """ Make sure we can't login with an inactive user """
        from pyramid_signup.models import User
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
            }, request_method='POST')

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

class TestRegisterController(UnitTestBase):
    def test_register_controller_extensions_with_mail(self):
        from pyramid_mailer.mailer import DummyMailer
        from pyramid_mailer.interfaces import IMailer
        from pyramid_signup.views import RegisterController
        from pyramid_signup.interfaces import ISURegisterSchema
        from pyramid_signup.interfaces import ISURegisterForm

        self.config.add_route('index', '/')

        request = testing.DummyRequest()

        getUtility = Mock()
        getUtility.return_value = True

        schema = Mock()
        form = Mock()

        self.config.registry.registerUtility(schema, ISURegisterSchema)
        self.config.registry.registerUtility(form, ISURegisterForm)
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        with patch('pyramid_signup.views.get_mailer') as get_mailer:
            RegisterController(request)
            assert get_mailer.called

        assert schema.called
        assert form.called

    def test_register_controller_extensions_without_mail(self):
        from pyramid_signup.views import RegisterController
        from pyramid_signup.interfaces import ISURegisterSchema
        from pyramid_signup.interfaces import ISURegisterForm

        self.config.add_route('index', '/')

        request = testing.DummyRequest()

        getUtility = Mock()
        getUtility.return_value = True

        schema = Mock()
        form = Mock()
        
        self.config.registry.settings['su.require_activation'] = False
        self.config.registry.registerUtility(schema, ISURegisterSchema)
        self.config.registry.registerUtility(form, ISURegisterForm)

        with patch('pyramid_signup.views.get_mailer') as get_mailer:
            RegisterController(request)
            assert not get_mailer.called

        schema.assert_called_once_with()
        assert form.called

    def test_register_loads_not_logged_in(self):
        from pyramid_signup.views import RegisterController
        from pyramid_mailer.mailer import DummyMailer
        from pyramid_mailer.interfaces import IMailer

        self.config.include('pyramid_signup')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        self.config.add_route('index', '/')

        request = testing.DummyRequest()
        request.user = None
        controller = RegisterController(request)
        response = controller.get()

        assert response.get('form', None)

    def test_register_redirects_if_logged_in(self):
        from pyramid_signup.views import RegisterController
        from pyramid_mailer.mailer import DummyMailer
        from pyramid_mailer.interfaces import IMailer

        self.config.include('pyramid_signup')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        self.config.add_route('index', '/')

        request = testing.DummyRequest()
        request.user = Mock()
        controller = RegisterController(request)
        response = controller.get()

        assert response.status_int == 302

    def test_register_creates_user(self):
        from pyramid_signup.views import RegisterController
        from pyramid_mailer.mailer import DummyMailer
        from pyramid_mailer.interfaces import IMailer
        from pyramid_signup.managers import UserManager

        self.config.include('pyramid_signup')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        self.config.add_route('index', '/')

        request = self.get_csrf_request(post={
            'Username': 'admin',
            'Password': {
                'value': 'test123',
                'confirm': 'test123',
            },
            'Email': 'sontek@gmail.com'
        }, request_method='POST')

        request.user = Mock()
        controller = RegisterController(request)
        response = controller.post()

        assert response.status_int == 302

        mgr = UserManager(request)
        user = mgr.get_by_username('admin')

        assert user != None

    def test_register_validation(self):
        from pyramid_signup.views import RegisterController
        from pyramid_mailer.mailer import DummyMailer
        from pyramid_mailer.interfaces import IMailer

        self.config.include('pyramid_signup')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        self.config.add_route('index', '/')

        request = self.get_csrf_request(request_method='POST')

        request.user = Mock()
        controller = RegisterController(request)
        response = controller.post()

        assert len(response['errors']) == 3
        assert 'There was a problem with your submission' in response['form']

    def test_register_existing_user(self):
        from pyramid_signup.views import RegisterController
        from pyramid_mailer.mailer import DummyMailer
        from pyramid_mailer.interfaces import IMailer
        from pyramid_signup.models import User

        self.config.include('pyramid_signup')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        self.config.add_route('index', '/')

        admin = User(username='sontek', password='temp')
        self.session.add(admin)
        self.session.flush()

        request = self.get_csrf_request(post={
            'Username': 'sontek',
            'Password': {
                'value': 'test123',
                'confirm': 'test123',
            },
            'Email': 'sontek@gmail.com'
        }, request_method='POST')

        flash = Mock()
        request.session.flash = flash

        controller = RegisterController(request)
        controller.post()

        flash.assert_called_with(u'That username is already used.', 'error')

    def test_register_no_email_validation(self):
        from pyramid_signup.views import RegisterController
        from pyramid_mailer.mailer import DummyMailer
        from pyramid_mailer.interfaces import IMailer
        from pyramid_signup.managers import UserManager

        self.config.include('pyramid_signup')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        self.config.add_route('index', '/')
        self.config.registry.settings['su.require_activation'] = False

        request = self.get_csrf_request(post={
            'Username': 'admin',
            'Password': {
                'value': 'test123',
                'confirm': 'test123',
            },
            'Email': 'sontek@gmail.com'
        }, request_method='POST')

        request.user = Mock()
        controller = RegisterController(request)
        response = controller.post()

        assert response.status_int == 302

        mgr = UserManager(request)
        user = mgr.get_by_username('admin')

        assert user.activated == True

    def test_registration_craps_out(self):
        from pyramid_signup.views import RegisterController
        from pyramid_mailer.interfaces import IMailer

        def send(message):
            raise Exception("I broke!")

        mailer = Mock()
        mailer.send = send

        self.config.include('pyramid_signup')
        self.config.registry.registerUtility(mailer, IMailer)

        self.config.add_route('index', '/')

        request = self.get_csrf_request(post={
            'Username': 'admin',
            'Password': {
                'value': 'test123',
                'confirm': 'test123',
            },
            'Email': 'sontek@gmail.com'
        }, request_method='POST')

        flash = Mock()
        request.session.flash = flash

        request.user = Mock()
        controller = RegisterController(request)
        controller.post()

        flash.assert_called_with('I broke!', 'error')

    def test_activate(self):
        from pyramid_signup.views import RegisterController
        from pyramid_signup.models import User
        from pyramid_signup.models import Activation
        from pyramid_mailer.interfaces import IMailer
        from pyramid_mailer.mailer import DummyMailer
        from pyramid_signup.managers import UserManager
        self.config.include('pyramid_signup')
        self.config.add_route('index', '/')

        self.config.registry.registerUtility(DummyMailer(), IMailer)

        user = User(username='sontek', password='temp')
        user.activation = Activation()

        self.session.add(user)
        self.session.flush()

        request = testing.DummyRequest()
        request.matchdict = Mock()
        get = Mock()
        get.return_value = user.activation.code
        request.matchdict.get = get

        controller = RegisterController(request)
        response = controller.activate()
        mgr = UserManager(request)
        user = mgr.get_by_username('sontek')

        assert user.activated
        assert response.status_int == 302

    def test_activate_invalid(self):
        from pyramid_signup.views import RegisterController
        from pyramid_signup.models import User
        from pyramid_signup.models import Activation
        from pyramid_mailer.interfaces import IMailer
        from pyramid_mailer.mailer import DummyMailer
        from pyramid_signup.managers import UserManager
        self.config.include('pyramid_signup')
        self.config.add_route('index', '/')

        self.config.registry.registerUtility(DummyMailer(), IMailer)

        user = User(username='sontek', password='temp')
        user.activation = Activation()

        self.session.add(user)
        self.session.flush()

        request = testing.DummyRequest()
        request.matchdict = Mock()
        get = Mock()
        get.return_value = 'invalid'
        request.matchdict.get = get

        controller = RegisterController(request)
        response = controller.activate()
        mgr = UserManager(request)
        user = mgr.get_by_username('sontek')

        assert not user.activated
        assert response.status_int == 404
