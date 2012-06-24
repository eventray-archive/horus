from pyramid import testing

from mock import Mock
from mock import patch

from horus.tests import UnitTestBase

class TestAuthController(UnitTestBase):
    def test_auth_controller_extensions(self):
        from horus.views import AuthController
        from horus.interfaces import IHorusLoginSchema
        from horus.interfaces import IHorusLoginForm

        self.config.add_route('index', '/')

        request = testing.DummyRequest()

        getUtility = Mock()
        getUtility.return_value = True

        schema = Mock()
        form = Mock()

        self.config.registry.registerUtility(schema, IHorusLoginSchema)
        self.config.registry.registerUtility(form, IHorusLoginForm)

        AuthController(request)

        assert schema.called
        assert form.called


    def test_login_loads(self):
        from horus.views import AuthController
        self.config.add_route('index', '/')
        self.config.include('horus')

        request = testing.DummyRequest()
        request.user = None
        view = AuthController(request)
        response = view.login()

        assert response.get('form', None)

    def test_login_redirects_if_logged_in(self):
        from horus.views import AuthController
        self.config.add_route('index', '/')
        self.config.include('horus')

        request = testing.DummyRequest()
        request.user = Mock()
        view = AuthController(request)

        response = view.login()
        assert response.status_int == 302

    def test_login_fails_empty(self):
        """ Make sure we can't login with empty credentials"""
        from horus.views import AuthController
        self.config.add_route('index', '/')
        self.config.include('horus')

        request = testing.DummyRequest(post={
            'submit': True,
        }, request_method='POST')

        view = AuthController(request)
        response = view.login()
        errors = response['errors']

        assert errors[0].node.name == u'csrf_token'
        assert errors[0].msg == u'Required'
        assert errors[1].node.name == u'Username'
        assert errors[1].msg == u'Required'
        assert errors[2].node.name == u'Password'
        assert errors[2].msg == u'Required'

    def test_csrf_invalid_fails(self):
        """ Make sure we can't login with a bad csrf """
        from horus.views import AuthController
        self.config.add_route('index', '/')
        self.config.include('horus')

        request = self.get_csrf_request(post={
                    'submit': True,
                    'login': 'admin',
                    'password': 'test123',
                    'csrf_token': 'abc2'
                }, request_method='POST')

        view = AuthController(request)

        response = view.login()

        errors = response['errors']

        assert errors[0].node.name == u'csrf_token'
        assert errors[0].msg == u'Invalid cross-site scripting token'


    def test_login_fails_bad_credentials(self):
        """ Make sure we can't login with bad credentials"""
        from horus.views import AuthController
        self.config.add_route('index', '/')
        self.config.include('horus')

        request = self.get_csrf_request(post={
                'submit': True,
                'Username': 'admin',
                'Password': 'test123',
            }, request_method='POST')

        flash = Mock()
        request.session.flash = flash

        view = AuthController(request)
        view.login()

        flash.assert_called_with(u'Invalid username or password.', 'error')

    def test_login_succeeds(self):
        """ Make sure we can login """
        from horus.models import User
        admin = User(username='sontek', password='temp')
        admin.activated = True

        self.session.add(admin)
        self.session.flush()

        from horus.views import AuthController
        self.config.add_route('index', '/')

        self.config.include('horus')

        request = self.get_csrf_request(post={
                'submit': True,
                'Username': 'sontek',
                'Password': 'temp',
            }, request_method='POST')

        view = AuthController(request)
        response = view.login()

        assert response.status_int == 302

    def test_inactive_login_fails(self):
        """ Make sure we can't login with an inactive user """
        from horus.models import User
        user = User(username='sontek', password='temp')

        self.session.add(user)
        self.session.flush()

        from horus.views import AuthController
        self.config.add_route('index', '/')
        self.config.include('horus')

        request = self.get_csrf_request(post={
                'submit': True,
                'Username': 'sontek',
                'Password': 'temp',
            }, request_method='POST')

        flash = Mock()

        request.session.flash = flash

        view = AuthController(request)
        view.login()

        flash.assert_called_with(u'Your account is not active, please check your e-mail.',
            'error')

    def test_logout(self):
        from horus.views import AuthController
        self.config.add_route('index', '/')
        self.config.include('horus')
        request = testing.DummyRequest()

        flash = Mock()
        invalidate = Mock()

        request.user = Mock()
        request.session = Mock()
        request.session.invalidate = invalidate
        request.session.flash = flash

        view = AuthController(request)
        with patch('horus.views.forget') as forget:
            with patch('horus.views.HTTPFound') as HTTPFound:
                view.logout()
                flash.assert_called_with(u'Logged out successfully.', 'success')
                forget.assert_called_with(request)
                assert invalidate.called
                assert HTTPFound.called

class TestRegisterController(UnitTestBase):
    def test_register_controller_extensions_with_mail(self):
        from pyramid_mailer.mailer import DummyMailer
        from pyramid_mailer.interfaces import IMailer
        from horus.views import RegisterController
        from horus.interfaces import IHorusRegisterSchema
        from horus.interfaces import IHorusRegisterForm

        self.config.add_route('index', '/')

        request = testing.DummyRequest()

        getUtility = Mock()
        getUtility.return_value = True

        schema = Mock()
        form = Mock()

        self.config.registry.registerUtility(schema, IHorusRegisterSchema)
        self.config.registry.registerUtility(form, IHorusRegisterForm)
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        with patch('horus.views.get_mailer') as get_mailer:
            RegisterController(request)
            assert get_mailer.called

        assert schema.called
        assert form.called

    def test_register_controller_extensions_without_mail(self):
        from horus.views import RegisterController
        from horus.interfaces import IHorusRegisterSchema
        from horus.interfaces import IHorusRegisterForm

        self.config.add_route('index', '/')

        request = testing.DummyRequest()

        getUtility = Mock()
        getUtility.return_value = True

        schema = Mock()
        form = Mock()
        
        self.config.registry.settings['su.require_activation'] = False
        self.config.registry.registerUtility(schema, IHorusRegisterSchema)
        self.config.registry.registerUtility(form, IHorusRegisterForm)

        with patch('horus.views.get_mailer') as get_mailer:
            RegisterController(request)
            assert not get_mailer.called

        schema.assert_called_once_with()
        assert form.called

    def test_register_loads_not_logged_in(self):
        from horus.views import RegisterController
        from pyramid_mailer.mailer import DummyMailer
        from pyramid_mailer.interfaces import IMailer

        self.config.include('horus')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        self.config.add_route('index', '/')

        request = testing.DummyRequest()
        request.user = None
        controller = RegisterController(request)
        response = controller.register()

        assert response.get('form', None)

    def test_register_redirects_if_logged_in(self):
        from horus.views import RegisterController
        from pyramid_mailer.mailer import DummyMailer
        from pyramid_mailer.interfaces import IMailer

        self.config.include('horus')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        self.config.add_route('index', '/')

        request = testing.DummyRequest()
        request.user = Mock()
        controller = RegisterController(request)
        response = controller.register()

        assert response.status_int == 302

    def test_register_creates_user(self):
        from horus.views import RegisterController
        from pyramid_mailer.mailer import DummyMailer
        from pyramid_mailer.interfaces import IMailer
        from horus.managers import UserManager

        self.config.include('horus')
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
        response = controller.register()

        assert response.status_int == 302

        mgr = UserManager(request)
        user = mgr.get_by_username('admin')

        assert user != None

    def test_register_validation(self):
        from horus.views import RegisterController
        from pyramid_mailer.mailer import DummyMailer
        from pyramid_mailer.interfaces import IMailer

        self.config.include('horus')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        self.config.add_route('index', '/')

        request = self.get_csrf_request(request_method='POST')

        request.user = Mock()
        controller = RegisterController(request)
        response = controller.register()

        assert len(response['errors']) == 3
        assert 'There was a problem with your submission' in response['form']

    def test_register_existing_user(self):
        from horus.views import RegisterController
        from pyramid_mailer.mailer import DummyMailer
        from pyramid_mailer.interfaces import IMailer
        from horus.models import User

        self.config.include('horus')
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
        controller.register()

        flash.assert_called_with(u'That username is already used.', 'error')

    def test_register_no_email_validation(self):
        from horus.views import RegisterController
        from pyramid_mailer.mailer import DummyMailer
        from pyramid_mailer.interfaces import IMailer
        from horus.managers import UserManager
        from horus.interfaces import IHorusSession
        from horus.events import NewRegistrationEvent

        self.config.include('horus')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        self.config.add_route('index', '/')
        self.config.registry.settings['su.require_activation'] = False

        def handle_registration(event):
            request = event.request
            session = request.registry.getUtility(IHorusSession)
            session.commit()

        self.config.add_subscriber(handle_registration, NewRegistrationEvent)


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
        response = controller.register()

        assert response.status_int == 302

        mgr = UserManager(request)
        user = mgr.get_by_username('admin')

        assert user.activated == True
        flash.assert_called_with('You have been registered, you may login now!', 'success')

    def test_registration_craps_out(self):
        from horus.views import RegisterController
        from pyramid_mailer.interfaces import IMailer

        def send(message):
            raise Exception("I broke!")

        mailer = Mock()
        mailer.send = send

        self.config.include('horus')
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
        controller.register()

        flash.assert_called_with('I broke!', 'error')

    def test_activate(self):
        from horus.views import RegisterController
        from horus.models import User
        from horus.models import Activation
        from pyramid_mailer.interfaces import IMailer
        from pyramid_mailer.mailer import DummyMailer
        from horus.managers import UserManager
        self.config.include('horus')
        self.config.add_route('index', '/')

        self.config.registry.registerUtility(DummyMailer(), IMailer)

        user = User(username='sontek', password='temp')
        user.activation = Activation()

        self.session.add(user)
        self.session.flush()

        request = testing.DummyRequest()
        request.matchdict = Mock()

        def get(key, default):
            if key == 'code':
                return user.activation.code
            else:
                return user.pk

        request.matchdict.get = get

        controller = RegisterController(request)
        response = controller.activate()
        mgr = UserManager(request)
        user = mgr.get_by_username('sontek')

        assert user.activated
        assert response.status_int == 302

    def test_activate_multiple_users(self):
        from horus.views import RegisterController
        from horus.models import User
        from horus.models import Activation
        from pyramid_mailer.interfaces import IMailer
        from pyramid_mailer.mailer import DummyMailer
        from horus.managers import UserManager
        from horus.managers import ActivationManager
        self.config.include('horus')
        self.config.add_route('index', '/')

        self.config.registry.registerUtility(DummyMailer(), IMailer)

        user = User(username='sontek', password='temp')
        user.activation = Activation()
        user1 = User(username='sontek1', password='temp')
        user1.activation = Activation()

        self.session.add(user)
        self.session.add(user1)
        self.session.flush()

        request = testing.DummyRequest()
        request.matchdict = Mock()

        def get(key, default):
            if key == 'code':
                return user1.activation.code
            else:
                return user1.pk

        request.matchdict.get = get

        controller = RegisterController(request)
        response = controller.activate()
        mgr = UserManager(request)
        user = mgr.get_by_username('sontek1')

        act_mgr = ActivationManager(request)
        activations = act_mgr.get_all()

        assert len(activations) == 1
        assert user.activated
        assert response.status_int == 302

    def test_activate_invalid(self):
        from horus.views import RegisterController
        from horus.models import User
        from horus.models import Activation
        from pyramid_mailer.interfaces import IMailer
        from pyramid_mailer.mailer import DummyMailer
        from horus.managers import UserManager
        self.config.include('horus')
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

    def test_activate_invalid_user(self):
        from horus.views import RegisterController
        from horus.models import User
        from horus.models import Activation
        from pyramid_mailer.interfaces import IMailer
        from pyramid_mailer.mailer import DummyMailer
        from horus.managers import UserManager
        self.config.include('horus')
        self.config.add_route('index', '/')

        self.config.registry.registerUtility(DummyMailer(), IMailer)

        bad_act = Activation()

        user = User(username='sontek', password='temp')
        user.activation = Activation()

        user2 = User(username='jessie', password='temp')
        user2.activation = bad_act

        self.session.add(user)
        self.session.add(user2)
        self.session.flush()

        request = testing.DummyRequest()
        request.matchdict = Mock()

        def get(val, ret):
            if val == 'code':
                return bad_act.code
            elif val == 'user_pk':
                return user.pk

        request.matchdict.get = get

        controller = RegisterController(request)
        response = controller.activate()
        mgr = UserManager(request)
        new_user1 = mgr.get_by_username('sontek')
        new_user2 = mgr.get_by_username('jessie')

        assert not new_user1.activated
        assert not new_user2.activated
        assert response.status_int == 404

class TestForgotPasswordController(UnitTestBase):
    def test_forgot_password_loads(self):
        from horus.views import ForgotPasswordController
        self.config.add_route('index', '/')
        self.config.include('horus')

        request = testing.DummyRequest()
        request.user = None
        view = ForgotPasswordController(request)
        response = view.forgot_password()

        assert response.get('form', None)

    def test_forgot_password_logged_in_redirects(self):
        from horus.views import ForgotPasswordController
        self.config.add_route('index', '/')
        self.config.include('horus')

        request = testing.DummyRequest()
        request.user = Mock()
        view = ForgotPasswordController(request)
        response = view.forgot_password()

        assert response.status_int == 302

    def test_forgot_password_valid_user(self):
        from horus.views import ForgotPasswordController
        from pyramid_mailer.interfaces import IMailer
        from pyramid_mailer.mailer import DummyMailer

        self.config.add_route('index', '/')
        self.config.include('horus')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        from horus.models import User

        user = User(username='sontek', password='temp', email='sontek@gmail.com')

        self.session.add(user)
        self.session.flush()


        request = self.get_csrf_request(post={
            'Email': 'sontek@gmail.com'
        }, request_method='POST')

        request.user = None

        flash = Mock()
        request.session.flash = flash

        view = ForgotPasswordController(request)
        response = view.forgot_password()

        flash.assert_called_with(u'Please check your e-mail to reset your password.', 'success')
        assert response.status_int == 302

    def test_forgot_password_invalid_password(self):
        from horus.views import ForgotPasswordController
        from pyramid_mailer.interfaces import IMailer
        from pyramid_mailer.mailer import DummyMailer

        self.config.add_route('index', '/')
        self.config.include('horus')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        from horus.models import User

        user = User(username='sontek', password='temp', email='sontek@gmail.com')

        self.session.add(user)
        self.session.flush()

        request = self.get_csrf_request(post={
            'Email': 'sontek'
        }, request_method='POST')

        request.user = None

        view = ForgotPasswordController(request)
        response = view.forgot_password()

        assert len(response['errors']) == 1

    def test_reset_password_loads(self):
        from horus.views import ForgotPasswordController
        from pyramid_mailer.interfaces import IMailer
        from pyramid_mailer.mailer import DummyMailer

        self.config.add_route('index', '/')
        self.config.include('horus')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        from horus.models import User
        from horus.models import Activation

        user = User(username='sontek', password='temp', email='sontek@gmail.com')
        user.activation = Activation()

        self.session.add(user)
        self.session.flush()

        request = testing.DummyRequest()

        request.matchdict = Mock()
        get = Mock()
        get.return_value = user.activation.code
        request.matchdict.get = get

        request.user = None

        view = ForgotPasswordController(request)
        response = view.reset_password()

        assert response.get('form', None)
        assert 'sontek' in response['form']

    def test_reset_password_valid_user(self):
        from horus.views import ForgotPasswordController
        from horus.interfaces import IHorusSession
        from horus.events import PasswordResetEvent
        from pyramid_mailer.interfaces import IMailer
        from pyramid_mailer.mailer import DummyMailer
        from horus.models import User
        from horus.models import Activation
        from horus.models import crypt


        self.config.add_route('index', '/')
        self.config.include('horus')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        user = User(username='sontek', password='temp', email='sontek@gmail.com')
        user.activation = Activation()

        self.session.add(user)
        self.session.flush()

        request = self.get_csrf_request(post={
            'Password': {
                'value': 'test123',
                'confirm': 'test123',
            },
        }, request_method='POST')

        request.matchdict = Mock()
        get = Mock()
        get.return_value = user.activation.code
        request.matchdict.get = get

        request.user = None

        flash = Mock()
        request.session.flash = flash

        def handle_password_reset(event):
            request = event.request
            session = request.registry.getUtility(IHorusSession)
            session.commit()

        self.config.add_subscriber(handle_password_reset, PasswordResetEvent)

        view = ForgotPasswordController(request)
        response = view.reset_password()

        assert not crypt.check(user.password, 'temp' + user.salt)
        assert response.status_int == 302

    def test_reset_password_invalid_password(self):
        from horus.views import ForgotPasswordController
        from pyramid_mailer.interfaces import IMailer
        from pyramid_mailer.mailer import DummyMailer

        self.config.add_route('index', '/')
        self.config.include('horus')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        from horus.models import User
        from horus.models import Activation

        user = User(username='sontek', password='temp', email='sontek@gmail.com')
        user.activation = Activation()

        self.session.add(user)
        self.session.flush()

        request = self.get_csrf_request(post={
            'Password': {
                'value': 't',
                'confirm': 't',
            },
        }, request_method='POST')

        request.matchdict = Mock()
        get = Mock()
        get.return_value = user.activation.code
        request.matchdict.get = get

        request.user = None

        flash = Mock()
        request.session.flash = flash

        view = ForgotPasswordController(request)
        response = view.reset_password()

        assert len(response['errors']) == 1

    def test_reset_password_empty_password(self):
        from horus.views import ForgotPasswordController
        from pyramid_mailer.interfaces import IMailer
        from pyramid_mailer.mailer import DummyMailer

        self.config.add_route('index', '/')
        self.config.include('horus')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        from horus.models import User
        from horus.models import Activation

        user = User(username='sontek', password='temp', email='sontek@gmail.com')
        user.activation = Activation()

        self.session.add(user)
        self.session.flush()

        request = self.get_csrf_request(request_method='POST')

        request.matchdict = Mock()
        get = Mock()
        get.return_value = user.activation.code
        request.matchdict.get = get

        request.user = None

        flash = Mock()
        request.session.flash = flash

        view = ForgotPasswordController(request)

        response = view.reset_password()

        assert len(response['errors']) == 1

    def test_invalid_reset_gets_404(self):
        from horus.views import ForgotPasswordController
        from pyramid_mailer.interfaces import IMailer
        from pyramid_mailer.mailer import DummyMailer

        self.config.add_route('index', '/')
        self.config.include('horus')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        from horus.models import User
        from horus.models import Activation

        user = User(username='sontek', password='temp', email='sontek@gmail.com')
        user.activation = Activation()

        self.session.add(user)
        self.session.flush()

        request = testing.DummyRequest()

        request.matchdict = Mock()
        get = Mock()
        get.return_value = 'b'
        request.matchdict.get = get

        request.user = None

        view = ForgotPasswordController(request)
        response = view.reset_password()

        assert response.status_int == 404

class TestProfileController(UnitTestBase):
    def test_profile_loads(self):
        from horus.views import ProfileController

        self.config.add_route('index', '/')
        self.config.include('horus')

        from horus.models import User

        user = User(username='sontek', password='temp', email='sontek@gmail.com',
            activated=True)

        self.session.add(user)
        self.session.flush()

        request = testing.DummyRequest()
        request.user = Mock()

        flash = Mock()
        request.session.flash = flash

        request.matchdict = Mock()
        get = Mock()
        get.return_value = user.pk
        request.matchdict.get = get


        view = ProfileController(request)

        response = view.profile()

        assert response.get('form', None)

    def test_profile_bad_pk(self):
        from horus.views import ProfileController

        self.config.add_route('index', '/')
        self.config.include('horus')

        from horus.models import User

        user = User(username='sontek', password='temp', email='sontek@gmail.com',
            activated=True)

        self.session.add(user)
        self.session.flush()

        request = testing.DummyRequest()
        request.user = Mock()

        flash = Mock()
        request.session.flash = flash

        request.matchdict = Mock()
        get = Mock()
        get.return_value = 99
        request.matchdict.get = get

        view = ProfileController(request)

        response = view.profile()

        assert response.status_int == 404

    def test_profile_update_profile_invalid(self):
        from horus.views import ProfileController

        self.config.add_route('index', '/')
        self.config.include('horus')

        from horus.models import User

        user = User(username='sontek', password='temp', email='sontek@gmail.com',
            activated=True)

        self.session.add(user)
        self.session.flush()

        request = self.get_csrf_request(request_method='POST') 
        request.user = user

        request.matchdict = Mock()
        get = Mock()
        get.return_value = user.pk
        request.matchdict.get = get


        flash = Mock()
        request.session.flash = flash

        view = ProfileController(request)

        response = view.profile()

        assert len(response['errors']) == 3

    def test_profile_update_profile(self):
        from horus.views import ProfileController
        from horus.managers import UserManager
        from horus.interfaces import IHorusSession
        from horus.events import ProfileUpdatedEvent
        from horus.models import crypt

        self.config.add_route('index', '/')
        self.config.include('horus')

        from horus.models import User

        user = User(username='sontek', password='temp', email='sontek@gmail.com',
            activated=True)

        self.session.add(user)
        self.session.flush()

        def handle_profile_updated(event):
            request = event.request
            session = request.registry.getUtility(IHorusSession)
            session.commit()

        self.config.add_subscriber(handle_profile_updated, ProfileUpdatedEvent)

        request = self.get_csrf_request(post={
            'First_Name': 'John',
            'Last_Name': 'Anderson',
            'Email': 'sontek@gmail.com',
        }, request_method='POST')

        request.user = user

        flash = Mock()
        request.session.flash = flash

        request.matchdict = Mock()
        get = Mock()
        get.return_value = user.pk
        request.matchdict.get = get

        view = ProfileController(request)
        view.profile()

        mgr = UserManager(request)
        new_user = mgr.get_by_pk(user.pk)

        assert new_user.first_name == 'John'
        assert new_user.last_name == 'Anderson'
        assert new_user.email == 'sontek@gmail.com'
        assert crypt.check(user.password, 'temp' + user.salt)

    def test_profile_update_password(self):
        from horus.views import ProfileController
        from horus.managers import UserManager
        from horus.interfaces import IHorusSession
        from horus.events import ProfileUpdatedEvent
        from horus.models import crypt

        self.config.add_route('index', '/')
        self.config.include('horus')

        from horus.models import User

        user = User(username='sontek', password='temp', email='sontek@gmail.com',
            activated=True)

        self.session.add(user)
        self.session.flush()

        def handle_profile_updated(event):
            request = event.request
            session = request.registry.getUtility(IHorusSession)
            session.commit()

        self.config.add_subscriber(handle_profile_updated, ProfileUpdatedEvent)


        request = self.get_csrf_request(post={
            'First_Name': 'John',
            'Last_Name': 'Anderson',
            'Email': 'sontek@gmail.com',
            'Password': {
                'value': 'test123',
                'confirm': 'test123',
            },
        }, request_method='POST')

        request.user = user

        request.matchdict = Mock()
        get = Mock()
        get.return_value = user.pk
        request.matchdict.get = get


        flash = Mock()
        request.session.flash = flash

        view = ProfileController(request)

        view.profile()
        mgr = UserManager(request)
        new_user = mgr.get_by_pk(user.pk)

        assert new_user.first_name == 'John'
        assert new_user.last_name == 'Anderson'
        assert new_user.email == 'sontek@gmail.com'
        assert not crypt.check(user.password, 'temp' + user.salt)
