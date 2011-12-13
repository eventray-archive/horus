def build_routes(config):
    """ Add routes to the config """
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('register', '/register')
    config.add_route('activate', '/activate/{code}')
    config.add_route('forgot_password', '/forgot_password')
    config.add_route('reset_password', '/reset_password/{code}')
    config.add_route('profile', '/profile')
