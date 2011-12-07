import colander
import deform

from pyramid_deform import CSRFSchema

class LoginSchema(CSRFSchema):
    Username = colander.SchemaNode(colander.String())
    Password = colander.SchemaNode(colander.String(),
        validator=colander.Length(min=2),
        widget=deform.widget.PasswordWidget())

