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
from pyramid_signup.managers import UserManager
from pyramid_signup.managers import ActivationManager
from pyramid_signup.models import User
from pyramid_signup.models import Activation
from pyramid_signup.lib import get_session

_ = TranslationStringFactory('pyramid_signup')

class BaseController(object):
    @property
    def request(self):
        # we defined this so that we can override the request in tests easily
        return self._request

    def __init__(self, request):
        self._request  = request

        self.settings = request.registry.settings
        self.using_tm = asbool(self.settings.get('su.using_tm', False))
        self.db = get_session(request)

class AuthController(BaseController):
    def __init__(self, request):
        super(AuthController, self).__init__(request)

        schema = request.registry.getUtility(ISULoginSchema)
        self.schema = schema().bind(request=self.request)

        form = request.registry.getUtility(ISULoginForm)

        self.login_redirect_view = route_url(self.settings.get('su.login_redirect', 'index'), request)
        self.logout_redirect_view = route_url(self.settings.get('su.logout_redirect', 'index'), request)

        self.form = form(self.schema)

    def authenticated(self, request, pk):
        """ This sets the auth cookies and redirects to the page defined
            in su.login_redirect, defaults to a view named 'index'
        """
        headers = remember(request, pk)
        request.session.flash(_('Logged in successfully.'), 'success')

        return HTTPFound(location=self.login_redirect_view, headers=headers)

    @view_config(route_name='login', request_method='POST', renderer='pyramid_signup:templates/login.mako')
    def post(self):
        if self.request.method == 'POST':
            try:
                controls = self.request.POST.items()
                captured = self.form.validate(controls)
            except deform.ValidationFailure, e:
                return {'form': e.render(), 'errors': e.error.children}

            username = captured['Username']
            password = captured['Password']

            mgr = UserManager(self.request)

            user = mgr.get_user(username, password)

            if user:
                if not user.activated:
                    self.request.session.flash(_(u'Your account is not active, please check your e-mail.'), 'error')
                    return {'form': self.form.render()}
                else:
                    return self.authenticated(self.request, user.pk)

            self.request.session.flash(_('Invalid username or password.'), 'error')

            return {'form': self.form.render(appstruct=captured)}

    @view_config(route_name='login', request_method='GET', renderer='pyramid_signup:templates/login.mako')
    def get(self):
        if self.request.user:
            return HTTPFound(location=self.login_redirect_view)

        return {'form': self.form.render()}

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

    @view_config(route_name='register', request_method='GET', renderer='pyramid_signup:templates/register.mako')
    def get(self):
        if self.request.user:
            return HTTPFound(location=self.register_redirect_view)

        return {'form': self.form.render()}

    @view_config(route_name='register', request_method='POST', renderer='pyramid_signup:templates/register.mako')
    def post(self):
        if self.request.method == 'POST':
            try:
                controls = self.request.POST.items()
                captured = self.form.validate(controls)
            except deform.ValidationFailure, e:
                return {'form': e.render(), 'errors': e.error.children}

            email = captured['Email']
            username = captured['Username']
            password = captured['Password']


            mgr = UserManager(self.request)
            user = mgr.get_by_username(username)

            if user:
                self.request.session.flash(_('That username is already used.'), 'error')
                return {'form': self.form.render(self.request.POST)}

            try:
                user = User(username=username, password=password, email=email)

                self.db.add(user)

                if self.require_activation:
                    user.activation = Activation()

                    if not self.using_tm:
                        self.db.commit()

                    body = pystache.render(_("Please activate your e-mail address by visiting {{ link }}"),
                        {
                            'link': route_url('activate', self.request, code=user.activation.code)
                        }
                    )

                    subject = _("Please active your e-mail address!")

                    message = Message(subject=subject, recipients=[user.email], body=body)
                    self.mailer.send(message)

                    self.request.session.flash(_('Please check your E-mail for an activation link'), 'success')
                else:
                    user.activated = True

                    if not self.using_tm:
                        self.db.commit()

            except Exception as exc:
                self.request.session.flash(exc.message, 'error')
                return {'form': self.form.render()}

            return HTTPFound(location=self.register_redirect_view)

    @view_config(route_name='activate')
    def activate(self):
        code = self.request.matchdict.get('code', None)
        act_mgr = ActivationManager(self.request)
        user_mgr = UserManager(self.request)

        activation = act_mgr.get_by_code(code)

        if activation:
            user = user_mgr.get_by_activation(activation)

            if user:
                self.db.delete(activation)
                user.activated = True
                self.db.add(user)

                if not self.using_tm:
                    self.db.commit()

                self.request.session.flash(_('Your e-mail address has been verified.'), 'success')
                return HTTPFound(location=self.activate_redirect_view)

        return HTTPNotFound()


