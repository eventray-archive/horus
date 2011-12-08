def build_routes(config):
    """ Add routes to the config """
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('register', '/register')


