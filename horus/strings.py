# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
    unicode_literals)
from zope.interface import implementer
from .interfaces import IUIStrings
from .models import _


@implementer(IUIStrings)
class UIStringsBase(object):  # TODO Continue building
    '''A class containing all GUI strings in the application, such that
    user apps can simply subclass and change whatever text they want.

    TODO: Document this!
    '''
    logout = _('You have logged out.')

    registration_email_exists = _("Sorry, an account with this "
        "e-mail already exists. Try logging in instead.")
    registration_username_exists = _("Sorry, an account with this "
        "username already exists.")

    reset_password_email_must_exist = _('We have no user with the email "{}". '
            "Try correcting this address or trying another.")
    reset_password_email_body = _("Someone has tried to reset your password. "
        "If it was you, click here:\n{{ link }}")
    reset_password_email_subject = _("Reset your password")
    # You don't want to say "E-mail not registered" or anything like that
    # because it gives spammers context:
    reset_password_email_sent = _('Please check your e-mail to finish '
        'resetting your password.')

__doc__ = UIStringsBase.__doc__
