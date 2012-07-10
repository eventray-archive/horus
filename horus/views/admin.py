from horus.views            import BaseController
from horus.schemas          import AdminUserSchema
from horus.forms            import HorusForm
from horus.resources        import RootFactory
from horus.interfaces       import IHorusUserClass
from pyramid.view           import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.i18n           import TranslationStringFactory

import deform

_ = TranslationStringFactory('horus')

class AdminController(BaseController):
    @view_config(
            route_name='horus_admin_users_create',
            renderer='horus:templates/admin/create_user.mako'
    )
    @view_config(
            route_name='horus_admin_users_edit',
            renderer='horus:templates/admin/create_user.mako'
    )
    def create_user(self):
        schema = AdminUserSchema()
        schema = schema.bind(request=self.request)
        form = HorusForm(schema)

        if self.request.method == 'GET':
            if isinstance(self.request.context, RootFactory):
                return dict(form=form)
            else:
                return dict(
                    form=form,
                    appstruct = self.request.context.__json__()
                )
        else:
            try:
                controls = self.request.POST.items()
                captured = form.validate(controls)
            except deform.ValidationFailure, e:
                return dict(form=e, errors=e.error.children)

            if isinstance(self.request.context, RootFactory):
                user = self.User(
                        user_name=captured['user_name'],
                        email=captured['email']
                )
            else:
                user = self.request.context

            if captured['password']:
                user.set_password(captured['password'])

            self.db.add(user)

            self.request.session.flash(_(u'The user was created'), 'success')

            return HTTPFound(
                location=self.request.route_url('horus_admin_users_index')
            )

    @view_config(
            route_name='horus_admin',
            renderer='horus:templates/admin/index.mako'
    )
    def index(self):
        return {}

    @view_config(
            route_name='horus_admin_users_index',
            renderer='horus:templates/admin/users_index.mako'
    )
    def users_index(self):
        return dict(users=self.User.get_all(self.request))
