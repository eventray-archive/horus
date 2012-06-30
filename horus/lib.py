from pyramid.security   import unauthenticated_userid
from horus.interfaces   import IHorusSession
from horus.interfaces   import IHorusUserClass

import hashlib
import random
import string

def generate_random_string(length):
    """Generate a generic hash key for the user to use"""
    m = hashlib.sha256()
    word = ''

    for i in xrange(length):
        word += random.choice(string.ascii_letters)

    m.update(word)

    return unicode(m.hexdigest()[:length])

def get_session(request):
    session = request.registry.getUtility(IHorusSession)

    return session

def get_user(request):
    pk = unauthenticated_userid(request)
    user_class = request.registry.queryUtility(IHorusUserClass)

    if pk is not None:
        return user_class.get_by_pk(request, pk)

def get_class_from_config(settings, key):
    if key in settings:
        user_modules = settings.get(key).split('.')
        module = '.'.join(user_modules[:-1])
        klass = user_modules[-1]
        imported_module = __import__(module, fromlist=[klass])
        imported_class = getattr(imported_module, klass)

        return imported_class
    else:
        raise Exception('Please provide a %s config option' % key)


def pluralize(singular):
    """Return plural form of given lowercase singular word (English only). Based on
    ActiveState recipe http://code.activestate.com/recipes/413172/

    >>> pluralize('')
    ''
    >>> pluralize('goose')
    'geese'
    >>> pluralize('dolly')
    'dollies'
    >>> pluralize('genius')
    'genii'
    >>> pluralize('jones')
    'joneses'
    >>> pluralize('pass')
    'passes'
    >>> pluralize('zero')
    'zeros'
    >>> pluralize('casino')
    'casinos'
    >>> pluralize('hero')
    'heroes'
    >>> pluralize('church')
    'churches'
    >>> pluralize('x')
    'xs'
    >>> pluralize('car')
    'cars'

    """
    ABERRANT_PLURAL_MAP = {
        'appendix': 'appendices',
        'barracks': 'barracks',
        'cactus': 'cacti',
        'child': 'children',
        'criterion': 'criteria',
        'deer': 'deer',
        'echo': 'echoes',
        'elf': 'elves',
        'embargo': 'embargoes',
        'focus': 'foci',
        'fungus': 'fungi',
        'goose': 'geese',
        'hero': 'heroes',
        'hoof': 'hooves',
        'index': 'indices',
        'knife': 'knives',
        'leaf': 'leaves',
        'life': 'lives',
        'man': 'men',
        'mouse': 'mice',
        'nucleus': 'nuclei',
        'person': 'people',
        'phenomenon': 'phenomena',
        'potato': 'potatoes',
        'self': 'selves',
        'syllabus': 'syllabi',
        'tomato': 'tomatoes',
        'torpedo': 'torpedoes',
        'veto': 'vetoes',
        'woman': 'women',
        }

    VOWELS = set('aeiou')

    if not singular:
        return ''
    plural = ABERRANT_PLURAL_MAP.get(singular)
    if plural:
        return plural
    root = singular
    try:
        if singular[-1] == 'y' and singular[-2] not in VOWELS:
            root = singular[:-1]
            suffix = 'ies'
        elif singular[-1] == 's':
            if singular[-2] in VOWELS:
                if singular[-3:] == 'ius':
                    root = singular[:-2]
                    suffix = 'i'
                else:
                    root = singular[:-1]
                    suffix = 'ses'
            else:
                suffix = 'es'
        elif singular[-2:] in ('ch', 'sh'):
            suffix = 'es'
        else:
            suffix = 's'
    except IndexError:
        suffix = 's'
    plural = root + suffix
    return plural
