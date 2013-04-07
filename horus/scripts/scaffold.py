#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
    unicode_literals)
import os
import sys

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)

import inspect
import horus.models
from horus.models import BaseModel


def usage(argv):  # pragma: no cover
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):  # pragma: no cover
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)

    base_scaffold = \
"""
from __future__ import (absolute_import, division, print_function,
    unicode_literals)

from horus.models import GroupMixin
from horus.models import UserMixin
from horus.models import UserGroupMixin
from horus.models import ActivationMixin
"""

    snippets = [base_scaffold]

    for name, obj in inspect.getmembers(horus.models):
        model_snippet = \
"""
class %(class_name)s(%(mixin)s, %(base)s):
    pass
"""
        if inspect.isclass(obj) and issubclass(obj, BaseModel) \
            and obj != BaseModel:
            class_name =  obj.__name__.replace('Mixin', '')
            mixin = obj.__name__
            #TODO: Allow them to define their base class in commandline
            base = 'Base'
            final = model_snippet % {
                'class_name': class_name,
                'mixin': mixin,
                'base': base
            }
            snippets.append(final)

    scaffold = '\n'.join(snippets)
    print(scaffold)

if __name__ == "__main__":  # pragma: no cover
    main()
