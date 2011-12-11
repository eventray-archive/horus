from zope.interface import Interface

class ISUSession(Interface):
    pass

class ISULoginSchema(Interface):
    pass

class ISULoginForm(Interface):
    pass

class ISURegisterSchema(Interface):
    pass

class ISURegisterForm(Interface):
    pass

class ISUForgotPasswordForm(Interface):
    pass

class ISUForgotPasswordSchema(Interface):
    pass

class ISUResetPasswordForm(Interface):
    pass

class ISUResetPasswordSchema(Interface):
    pass
