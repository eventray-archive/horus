import deform

class SubmitForm(deform.Form):
    def __init__(self, *args, **kwargs):

        if not kwargs.get('buttons'):
            kwargs['buttons'] = ('submit', )

        super(SubmitForm, self).__init__(*args, **kwargs)

