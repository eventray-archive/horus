import colander
import deform

from pyramid_deform import CSRFSchema

class LoginSchema(CSRFSchema):
    Username = colander.SchemaNode(colander.String())
    Password = colander.SchemaNode(colander.String(),
        validator=colander.Length(min=2),
        widget=deform.widget.PasswordWidget())

class RegisterSchema(CSRFSchema):
    Username = colander.SchemaNode(colander.String())
    Email = colander.SchemaNode(colander.String(),
        validator=colander.Email())
    Password = colander.SchemaNode(colander.String(),
        validator=colander.Length(min=2),
        widget=deform.widget.CheckedPasswordWidget())

class ForgotPasswordSchema(CSRFSchema):
    Email = colander.SchemaNode(colander.String(),
        validator=colander.Email())

class ResetPasswordSchema(CSRFSchema):
    Username = colander.SchemaNode(colander.String(),
            widget=deform.widget.TextInputWidget(template='readonly/textinput'),
            missing=colander.null,
    )
    Password = colander.SchemaNode(colander.String(),
        validator=colander.Length(min=2),
        widget=deform.widget.CheckedPasswordWidget())

