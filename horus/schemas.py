# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
    unicode_literals)
import colander
import deform

from pyramid_deform import CSRFSchema


class LoginSchema(CSRFSchema):
    username = colander.SchemaNode(colander.String())
    password = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(min=2),
        widget=deform.widget.PasswordWidget()
    )


class RegisterSchema(CSRFSchema):
    username = colander.SchemaNode(colander.String())
    email = colander.SchemaNode(colander.String(), validator=colander.Email())
    password = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(min=2),
        widget=deform.widget.CheckedPasswordWidget()
    )


class ForgotPasswordSchema(CSRFSchema):
    email = colander.SchemaNode(colander.String(), validator=colander.Email())


class ResetPasswordSchema(CSRFSchema):
    username = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.TextInputWidget(template='readonly/textinput'),
        missing=colander.null,
    )
    password = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(min=2),
        widget=deform.widget.CheckedPasswordWidget()
    )


class ProfileSchema(CSRFSchema):
    username = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.TextInputWidget(template='readonly/textinput'),
        missing=colander.null,
    )
    email = colander.SchemaNode(colander.String(), validator=colander.Email())
    password = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(min=2),
        widget=deform.widget.CheckedPasswordWidget(),
        missing=colander.null
    )


class AdminUserSchema(CSRFSchema):
    username = colander.SchemaNode(colander.String())
    email = colander.SchemaNode(
        colander.String(),
        validator=colander.Email()
    )
    password = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(min=2),
        widget=deform.widget.CheckedPasswordWidget(),
        missing=colander.null
    )
