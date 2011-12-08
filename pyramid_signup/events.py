class NewRegistrationEvent(object):
    def __init__(self, request, user, activation, values):
        self.user = user
        self.activation = activation
        self.values = values
        self.request = request
