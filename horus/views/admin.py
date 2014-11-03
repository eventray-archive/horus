# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import deform
from pyramid.view           import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound
from horus.lib              import FlashMessage
from horus.views            import BaseController
from horus.schemas          import AdminUserSchema
from horus.forms            import HorusForm
from horus.resources        import RootFactory


@view_defaults(permission='group:admin')
class AdminController(BaseController):
    @view_config(
        route_name='admin_users_create',
        renderer='horus:templates/admin/create_user.mako'
    )
    @view_config(
        route_name='admin_users_edit',
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
                    appstruct=self.request.context.__json__(self.request)
                )
        else:
            try:
                controls = self.request.POST.items()
                captured = form.validate(controls)
            except deform.ValidationFailure as e:
                return dict(form=e, errors=e.error.children)

            if isinstance(self.request.context, RootFactory):
                user = self.User(
                    username=captured['username'],
                    email=captured['email']
                )
            else:
                user = self.request.context

            if captured['password']:
                user.password = captured['password']

            self.db.add(user)

            FlashMessage(self.request, self.Str.admin_create_user_done,
                         'success')

            return HTTPFound(
                location=self.request.route_url('admin_users_index')
            )

    @view_config(
        route_name='admin',
        renderer='horus:templates/admin/index.mako'
    )
    def index(self):
        return {}

    @view_config(
        route_name='admin_users_index',
        renderer='horus:templates/admin/users_index.mako'
    )
    def users_index(self):
        return dict(users=self.User.get_all(self.request))
