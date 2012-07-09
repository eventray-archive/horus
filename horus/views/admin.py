from horus.views            import BaseController
from horus.schemas          import AdminUserSchema
from horus.forms            import HorusForm
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
    def create_user(self):
        schema = AdminUserSchema()
        schema = schema.bind(request=self.request)
        form = HorusForm(schema)

        if self.request.method == 'GET':
            return dict(form=form)
        else:
            try:
                controls = self.request.POST.items()
                captured = form.validate(controls)
            except deform.ValidationFailure, e:
                return dict(form=e, errors=e.error.children)

            user = self.User(
                    user_name=captured['User_name'],
                    email=captured['Email']
            )

            user.set_password(captured['Password'])

            self.db.add(user)

            self.request.session.flash(_(u'The user was created'), 'success')

            return HTTPFound(
                location=self.request.route_url('horus_admin_users_list')
            )

    @view_config(
            route_name='horus_admin_users_list',
            renderer='horus:templates/admin/users_list.mako'
    )
    def list(self):
        return dict(users=self.User.get_all(self.request))
