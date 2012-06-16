import hashlib
import random
import string

from horus.interfaces import ISUSession

def gen_hash_key(length):
    """Generate a generic hash key for the user to use"""
    m = hashlib.sha256()
    word = ''

    for i in xrange(length):
        word += random.choice(string.ascii_letters)

    m.update(word)

    return unicode(m.hexdigest()[:length])

def get_session(request):
    session = request.registry.getUtility(ISUSession)

    return session
