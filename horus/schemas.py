# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
    unicode_literals)
import colander as c
import deform
import deform.widget as w
from hem.db import get_session
from hem.schemas import CSRFSchema
from .interfaces import IUserClass, IUIStrings
from .models import _


class LoginSchema(CSRFSchema):
    username = c.SchemaNode(c.String())
    password = c.SchemaNode(c.String(), validator=c.Length(min=2),
        widget=deform.widget.PasswordWidget())


class RegisterSchema(CSRFSchema):
    username = c.SchemaNode(c.String())
    email = c.SchemaNode(c.String(), validator=c.Email())
    password = c.SchemaNode(c.String(), validator=c.Length(min=2),
        widget=deform.widget.CheckedPasswordWidget())


def email_exists(node, val):
    '''Colander validator that ensures a User exists with the email.'''
    req = node.bindings['request']
    Str = req.registry.getUtility(IUIStrings)
    User = req.registry.getUtility(IUserClass)
    exists = get_session(req).query(User).filter(User.email.ilike(val)).count()
    if not exists:
        raise c.Invalid(node, Str.reset_password_email_must_exist.format(val))


class ForgotPasswordSchema(CSRFSchema):
    email = c.SchemaNode(c.Str(), title=_('Email'),
        validator=c.All(c.Email(), email_exists),
        # type='email' will render an HTML5 email field
        # if you use deform_bootstrap_extra:
        widget=w.TextInputWidget(size=40, maxlength=260, type='email'),
        description=_("The email address under which you have your account. "
            "Example: joe@example.com"))


class ResetPasswordSchema(CSRFSchema):
    username = c.SchemaNode(c.String(), missing=c.null,
        widget=deform.widget.TextInputWidget(template='readonly/textinput'))
    password = c.SchemaNode(c.String(),  validator=c.Length(min=2),
        widget=deform.widget.CheckedPasswordWidget())


class ProfileSchema(CSRFSchema):
    username = c.SchemaNode(c.String(),
        widget=deform.widget.TextInputWidget(template='readonly/textinput'),
        missing=c.null)
    email = c.SchemaNode(c.String(), validator=c.Email())
    password = c.SchemaNode(c.String(), validator=c.Length(min=2),
        widget=deform.widget.CheckedPasswordWidget(), missing=c.null)


class AdminUserSchema(CSRFSchema):
    username = c.SchemaNode(c.String())
    email = c.SchemaNode(c.String(), validator=c.Email())
    password = c.SchemaNode(c.String(), validator=c.Length(min=2),
        widget=deform.widget.CheckedPasswordWidget(), missing=c.null)
