#!/usr/bin/env python
import os
import sys
import transaction
from getpass import getpass

from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)

#from horus.models import User
#from horus.models import SUEntity

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

def usage(argv):# pragma: no cover 
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd)) 
    sys.exit(1)

def main(argv=sys.argv): # pragma: no cover
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    session = DBSession(bind=engine)
    SUEntity.metadata.drop_all(engine)
    SUEntity.metadata.create_all(engine)

    username = raw_input("What is your username?: ").decode('utf-8')
    email = raw_input("What is your email?: ").decode('utf-8')
    password = getpass("What is your password?: ").decode('utf-8')


    with transaction.manager:
        admin = User(username=username, password=password, email=email, activated=True)
        session.add(admin)

if __name__ == "__main__": # pragma: no cover
    main()
