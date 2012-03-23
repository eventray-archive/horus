from pyramid.view import view_config
from pyramid.url import route_url
from pyramid.i18n import TranslationStringFactory
from pyramid.security import remember
from pyramid.security import forget
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from pyramid.settings import asbool

import deform
import pystache

from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

from pyramid_signup.interfaces import ISULoginForm
from pyramid_signup.interfaces import ISULoginSchema
from pyramid_signup.interfaces import ISURegisterForm
from pyramid_signup.interfaces import ISURegisterSchema
from pyramid_signup.interfaces import ISUForgotPasswordForm
from pyramid_signup.interfaces import ISUForgotPasswordSchema
from pyramid_signup.interfaces import ISUResetPasswordForm
from pyramid_signup.interfaces import ISUResetPasswordSchema
from pyramid_signup.interfaces import ISUProfileForm
from pyramid_signup.interfaces import ISUProfileSchema
from pyramid_signup.managers import UserManager
from pyramid_signup.managers import ActivationManager
from pyramid_signup.models import User
from pyramid_signup.models import Activation
from pyramid_signup.lib import get_session
from pyramid_signup.events import NewRegistrationEvent
from pyramid_signup.events import RegistrationActivatedEvent
from pyramid_signup.events import PasswordResetEvent
from pyramid_signup.events import ProfileUpdatedEvent

_ = TranslationStringFactory('pyramid_signup')

def authenticated(request, pk):
    """ This sets the auth cookies and redirects to the page defined
        in su.login_redirect, defaults to a view named 'index'
    """
    settings = request.registry.settings
    headers = remember(request, pk)
    autologin = asbool(settings.get('su.autologin', False))

    if not autologin:
        request.session.flash(_('Logged in successfully.'), 'success')

    login_redirect_view = route_url(settings.get('su.login_redirect', 'index'), request)

    return HTTPFound(location=login_redirect_view, headers=headers)

def create_activation(request, user):
    db = get_session(request)
    activation = Activation()

    db.add(activation)
    user.activation = activation

    db.flush()

    body = pystache.render(_("Please activate your e-mail address by visiting {{ link }}"),
        {
            'link': request.route_url('activate', user_pk=user.pk, code=user.activation.code)
        }
    )

    subject = _("Please active your e-mail address!")

    message = Message(subject=subject, recipients=[user.email], body=body)

    mailer = get_mailer(request)
    mailer.send(message)


class BaseController(object):
    @property
    def request(self):
        # we defined this so that we can override the request in tests easily
        return self._request

    def __init__(self, request):
        self._request  = request

        self.settings = request.registry.settings
        self.db = get_session(request)

class AuthController(BaseController):
    def __init__(self, request):
        super(AuthController, self).__init__(request)

        schema = request.registry.getUtility(ISULoginSchema)
        self.schema = schema().bind(request=self.request)

        form = request.registry.getUtility(ISULoginForm)

        self.login_redirect_view = route_url(self.settings.get('su.login_redirect', 'index'), request)
        self.logout_redirect_view = route_url(self.settings.get('su.logout_redirect', 'index'), request)
        self.require_activation = asbool(self.settings.get('su.require_activation', True))

        self.form = form(self.schema)


    @view_config(route_name='login', renderer='pyramid_signup:templates/login.mako')
    def login(self):
        if self.request.method == 'GET':
            if self.request.user:
                return HTTPFound(location=self.login_redirect_view)

            return {'form': self.form.render()}
        elif self.request.method == 'POST':
            try:
                controls = self.request.POST.items()
                captured = self.form.validate(controls)
            except deform.ValidationFailure, e:
                return {'form': e.render(), 'errors': e.error.children}

            username = captured['Username']
            password = captured['Password']

            mgr = UserManager(self.request)

            allow_email_auth = self.settings.get('su.allow_email_auth', False)

            user = mgr.get_user(username, password)

            if allow_email_auth:
                if not user:
                    user = mgr.get_by_email_password(username, password)

            if user:
                if self.require_activation:
                    if not user.activated:
                        self.request.session.flash(_(u'Your account is not active, please check your e-mail.'), 'error')
                        return {'form': self.form.render()}

                return authenticated(self.request, user.pk)

            self.request.session.flash(_('Invalid username or password.'), 'error')

            return {'form': self.form.render(appstruct=captured)}

    @view_config(permission='view', route_name='logout')
    def logout(self):
        """
        Removes the auth cookies and redirects to the view defined in 
        su.lgout_redirect, defaults to a view named 'index'
        """
        self.request.session.invalidate()
        self.request.session.flash(_('Logged out successfully.'), 'success')
        headers = forget(self.request)

        return HTTPFound(location=self.logout_redirect_view, headers=headers)


class ForgotPasswordController(BaseController):
    def __init__(self, request):
        super(ForgotPasswordController, self).__init__(request)

        self.forgot_password_redirect_view = route_url(self.settings.get('su.forgot_password_redirect', 'index'), request)
        self.reset_password_redirect_view = route_url(self.settings.get('su.reset_password_redirect', 'index'), request)

    @view_config(route_name='forgot_password', renderer='pyramid_signup:templates/forgot_password.mako')
    def forgot_password(self):
        schema = self.request.registry.getUtility(ISUForgotPasswordSchema)
        schema = schema().bind(request=self.request)

        form = self.request.registry.getUtility(ISUForgotPasswordForm)
        form = form(schema)

        if self.request.method == 'GET':
            if self.request.user:
                return HTTPFound(location=self.forgot_password_redirect_view)

            return {'form': form.render()}

        elif self.request.method == 'POST':
            try:
                controls = self.request.POST.items()
                captured = form.validate(controls)
            except deform.ValidationFailure, e:
                return {'form': e.render(), 'errors': e.error.children}

            email = captured['Email']

            mgr = UserManager(self.request)
            user = mgr.get_by_email(email)
            activation = Activation()
            self.db.add(activation)

            user.activation = activation

            if user:
                mailer = get_mailer(self.request)
                body = pystache.render(_("Someone has tried to reset your password, if this was you click here: {{ link }}"),
                    {
                        'link': route_url('reset_password', self.request, code=user.activation.code)
                    }
                )

                subject = _("Do you want to reset your password?")

                message = Message(subject=subject, recipients=[user.email], body=body)
                mailer.send(message)

        # we don't want to say "E-mail not registered" or anything like that
        # because it gives spammers context
        self.request.session.flash(_('Please check your e-mail to reset your password.'), 'success')
        return HTTPFound(location=self.reset_password_redirect_view)

    @view_config(route_name='reset_password', renderer='pyramid_signup:templates/reset_password.mako')
    def reset_password(self):
        schema = self.request.registry.getUtility(ISUResetPasswordSchema)
        schema = schema().bind(request=self.request)

        form = self.request.registry.getUtility(ISUResetPasswordForm)
        form = form(schema)

        code = self.request.matchdict.get('code', None)
        act_mgr = ActivationManager(self.request)
        user_mgr = UserManager(self.request)

        activation = act_mgr.get_by_code(code)

        if activation:
            user = user_mgr.get_by_activation(activation)

            if user:
                if self.request.method == 'GET':
                        return {
                            'form': form.render(
                                appstruct=dict(
                                    Username=user.username
                                )
                            )
                        }

                elif self.request.method == 'POST':
                    try:
                        controls = self.request.POST.items()
                        captured = form.validate(controls)
                    except deform.ValidationFailure, e:
                        return {'form': e.render(), 'errors': e.error.children}

                    password = captured['Password']

                    user.password = password
                    self.db.add(user)
                    self.db.delete(activation)

                    self.request.registry.notify(
                        PasswordResetEvent(self.request, user, password)
                    )

                    self.request.session.flash(_('Your password has been reset!'), 'success')

                    return HTTPFound(location=self.reset_password_redirect_view)

        return HTTPNotFound()


class RegisterController(BaseController):
    def __init__(self, request):
        super(RegisterController, self).__init__(request)
        schema = request.registry.getUtility(ISURegisterSchema)
        self.schema = schema().bind(request=self.request)

        form = request.registry.getUtility(ISURegisterForm)
        self.form = form(self.schema)

        self.register_redirect_view = route_url(self.settings.get('su.register_redirect', 'index'), request)
        self.activate_redirect_view = route_url(self.settings.get('su.activate_redirect', 'index'), request)

        self.require_activation = asbool(self.settings.get('su.require_activation', True))

        if self.require_activation:
            self.mailer = get_mailer(request)

    @view_config(route_name='register', renderer='pyramid_signup:templates/register.mako')
    def register(self):
        if self.request.method == 'GET':
            if self.request.user:
                return HTTPFound(location=self.register_redirect_view)

            return {'form': self.form.render()}
        elif self.request.method == 'POST':
            try:
                controls = self.request.POST.items()
                captured = self.form.validate(controls)
            except deform.ValidationFailure, e:
                return {'form': e.render(), 'errors': e.error.children}

            email = captured['Email']
            username = captured['Username']
            password = captured['Password']


            mgr = UserManager(self.request)
            user = mgr.get_by_username_or_email(username, email)

            autologin = asbool(self.settings.get('su.autologin', False))

            if user:
                if user.username == username:
                    self.request.session.flash(_('That username is already used.'), 'error')
                elif user.email == email:
                    self.request.session.flash(_('That e-mail is already used.'), 'error')

                return {'form': self.form.render(self.request.POST)}

            activation = None

            try:
                user = User(username=username, password=password, email=email)

                self.db.add(user)

                if self.require_activation:
                    # SEND EMAIL ACTIVATION
                    create_activation(self.request, user)
                    self.request.session.flash(_('Please check your E-mail for an activation link'), 'success')
                else:
                    if not autologin:
                        self.request.session.flash(_('You have been registered, you may login now!'), 'success')

            except Exception as exc:
                self.request.session.flash(exc.message, 'error')
                return {'form': self.form.render()}

            self.request.registry.notify(
                NewRegistrationEvent(self.request, user, activation,
                    captured)
            )


            if autologin:
                self.db.flush()

                return authenticated(self.request, user.pk)

            return HTTPFound(location=self.register_redirect_view)

    @view_config(route_name='activate')
    def activate(self):
        code = self.request.matchdict.get('code', None)
        user_pk = self.request.matchdict.get('user_pk', None)
        act_mgr = ActivationManager(self.request)
        user_mgr = UserManager(self.request)

        activation = act_mgr.get_by_code(code)

        if activation:
            user = user_mgr.get_by_pk(user_pk)

            if user.activation != activation:
                return HTTPNotFound()

            if user:
                self.db.delete(activation)
                user.activated = True
                self.db.add(user)
                self.db.flush()

                self.request.registry.notify(
                    RegistrationActivatedEvent(self.request, user, activation)
                )

                self.request.session.flash(_('Your e-mail address has been verified.'), 'success')
                return HTTPFound(location=self.activate_redirect_view)

        return HTTPNotFound()


class ProfileController(BaseController):
    def __init__(self, request):
        super(ProfileController, self).__init__(request)

        schema = self.request.registry.getUtility(ISUProfileSchema)
        self.schema = schema().bind(request=self.request)

        form = self.request.registry.getUtility(ISUProfileForm)
        self.form = form(self.schema)


    @view_config(route_name='profile', renderer='pyramid_signup:templates/profile.mako')
    def profile(self):
        pk = self.request.matchdict.get('user_pk', None)

        mgr = UserManager(self.request)

        user = mgr.get_by_pk(pk)

        if not user:
            return HTTPNotFound()

        return {'user': user}

    @view_config(permission='access_user', route_name='edit_profile',
        renderer='pyramid_signup:templates/edit_profile.mako')
    def edit_profile(self):
        user = self.request.context

        if not user:
            return HTTPNotFound()

        if self.request.method == 'GET':
            username = user.username
            first_name = user.first_name
            last_name = user.last_name
            email = user.email

            return {
                    'form': self.form.render(
                        appstruct= dict(
                            Username=username,
                            First_Name=first_name if first_name else '',
                            Last_Name=last_name if last_name else '',
                            Email=email if email else '',
                        )
                    )
                }
        elif self.request.method == 'POST':
            try:
                controls = self.request.POST.items()
                captured = self.form.validate(controls)
            except deform.ValidationFailure, e:
                # We pre-populate username
                e.cstruct['Username'] = user.username
                return {'form': e.render(), 'errors': e.error.children}

            user.first_name = captured.get('First_Name', '')
            user.last_name = captured.get('Last_Name', '')

            email = captured.get('Email', None)

            if email:
                mgr = UserManager(self.request)
                email_user = mgr.get_by_email(email)

                if email_user:
                    if email_user.pk != user.pk:
                        self.request.session.flash(_('That e-mail is already used.'), 'error')

                        return HTTPFound(location=self.request.url)

                user.email = email

            password = captured.get('Password')

            if password:
                user.password = password

            self.request.session.flash(_('Profile successfully updated.'), 'success')

            self.db.add(user)

            self.request.registry.notify(
                ProfileUpdatedEvent(self.request, user, captured)
            )

            return HTTPFound(location=self.request.url)
