import hashlib
import random
import string

def gen_hash_key(length):
    """Generate a generic hash key for the user to use"""
    m = hashlib.sha256()
    word = ''

    for i in xrange(length):
        word += random.choice(string.ascii_letters)

    m.update(word)

    return unicode(m.hexdigest()[:length])
