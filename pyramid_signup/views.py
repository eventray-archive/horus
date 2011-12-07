from pyramid.view import view_config
from pyramid.url import route_url
from pyramid.i18n import TranslationStringFactory
from pyramid.security import remember
from pyramid.security import forget
from pyramid.httpexceptions import HTTPFound


import deform

from pyramid_signup.interfaces import ISULoginForm
from pyramid_signup.interfaces import ISULoginSchema
from pyramid_signup.schemas import LoginSchema
from pyramid_signup.models import User

_ = TranslationStringFactory('pyramid_signup')

class AuthController(object):
    @property
    def request(self):
        # we defined this so that we can override the request in tests easily
        return self._request

    def __init__(self, request):
        self._request  = request

        schema = request.registry.getUtility(ISULoginSchema)
        if not schema:
            schema = LoginSchema

        self.schema = schema().bind(request=self.request)

        form = request.registry.getUtility(ISULoginForm)

        if not form:
            form = deform.Form

        self.form = form(self.schema)

    def authenticated(request, pk):
        """ This sets the auth cookies and redirects to the page defined
            in su.login_redirect, defaults to a view named 'index'
        """
        headers = remember(request, pk)
        settings = request.registry.settings
        redirect_view = route_url(settings.get('su.login_redirect', 'index'), request)
        request.session.flash(_('Logged in successfully.'), 'success')

        return HTTPFound(location=redirect_view, headers=headers)

    @view_config(permission='view', route_name='login', request_method='POST', renderer='pyramid_signup:templates/login.mako')
    def post(self):
        if 'submit' in self.request.POST:
            try:
                controls = self.request.POST.items()
                captured = self.form.validate(controls)
            except deform.ValidationFailure, e:
                return {'form': e.render(), 'errors': e.error.children}

            username = captured['Username']
            password = captured['Password']

            user = User.check_password(username, password)

            if user:
                if not user.activated:
                    self.request.session.flash(_(u'Your account is not active, please check your e-mail.'), 'error')
                    return {'form': self.form.render()}
                else:
                    return self.authenticated(self.request, user.pk)

            self.request.session.flash(_('Invalid username or password.'), 'error')

            return {'form': self.form.render(appstruct=captured)}

    @view_config(permission='view', route_name='login', request_method='GET', renderer='pyramid_signup:templates/login.mako')
    def get(self):
        if self.request.user:
            return HTTPFound(location=self.get_main_view())

        return {'form': self.form.render()}

    @view_config(permission='authed', route_name='logout')
    def logout(self):
        """
        Removes the auth cookies and redirects to the view defined in 
        su.lgout_redirect, defaults to a view named 'index'
        """
        self.request.session.invalidate()
        self.request.session.flash(_('Logged out successfully.'), 'success')
        headers = forget(self.request)

        settings = self.request.registry.settings
        redirect_view = route_url(settings.get('su.logout_redirect', 'index'),
            self.request)

        return HTTPFound(location=route_url(redirect_view, self.request),
                        headers=headers)
