Getting Started
=====================
First, Install the dependencies of the project:

>  $ pip install -r requirements.txt
>
>  $ python setup.py develop

Next, run our console script to setup the database:

> $ su_setup <your app config.ini>

Finally, to include pyramid_signup in your project, in your apps configuration,
you should include the package pyramid_mailer for the validation e-mail and forgot
password e-mail and tell pyramid_signup which session to use for the database objects.

``` python
 config.include('pyramid_mailer')
 from pyramid_signup.interfaces import ISUSession
 config.registry.registerUtility(DBSession, ISUSession)
 config.include('pyramid_signup')
 ```

pyramid_signup does not require pyramid_tm or the ZopeTransactionManager with your
session but if you do not use them you do have to take one extra step, we don't commit
transactions for you because that just wouldn't be nice!

All you have to do is to subscribe to the extension events and commit the session yourself,
this also gives you the ability to do some extra processing before processing is finished:

``` python
from pyramid_signup.events import PasswordResetEvent
from pyramid_signup.events import NewRegistrationEvent

def handle_request(event):
  request = event.request
  session = request.registry.getUtility(ISUSession)
  session.commit()

  self.config.add_subscriber(handle_request, PasswordResetEvent)
  self.config.add_subscriber(handle_request, NewRegistrationEvent)
```



Extending pyramid_signup
=============================
If you would like to modify any of the forms in pyramid signup, you just need
to register the new deform class to use in the registry.

The interaces you have available to override from pyramid_signup.interfaces:

>  ISULoginForm
>
>  ISURegisterForm
>
>  ISUForgotPasswordForm
>
>  ISUResetPasswordForm
>

This is how you would do it (uniform being a custom deform Form class):

>  config.registry.registerUtility(UNIForm, ISULoginForm)
>

If you would like to override the templates you can use pyramid's override asset 
functionality:

>    config.override_asset(to_override='pyramid_signup:templates/template.mako', override_with='your_package:templates/anothertemplate.mako')

The templates you have available to override are:

>  login.mako
>
>  register.mako
>
>  forgot_password.mako
>
>  reset_password.mako
>

If you would like to override the templates with Jinja2, you just have to override
the view configuration:

``` python

config.add_view('pyramid_signup.views.AuthController', attr='login', route_name='login',
    renderer='yourapp:templates/login.jinja2')
config.add_view('pyramid_signup.views.ForgotPasswordController', attr='forgot_password',
    route_name='forgot_password', renderer='yourapp:templates/forgot_password.jinja2')
config.add_view('pyramid_signup.views.ForgotPasswordController', attr='reset_password',
    route_name='reset_password', renderer='yourapp:templates/reset_password.jinja2')
config.add_view('pyramid_signup.views.RegisterController', attr='register',
    route_name='register', renderer='yourapp:templates/register.jinja2')

```

Development
=====================
If you would like to help make any changes to pyramid_signup, you can run its
unit tests with py.test:

> $ py.test

and to check test coverage:

> $ py.test --cov-report term-missing --cov pyramid_signup

you might also consider running the tests in parallel:

> $ py.test -n4

