from pyramid_signup.tests import UnitTestBase

class TestInterfaces(UnitTestBase):
    def test_susession(self):
        """ Shouldn't be able to instantiate the interface """
        from pyramid_signup.interfaces import ISUSession

        def make_session():
            ISUSession('1')

        self.assertRaises(TypeError, make_session)

    def test_suloginschema(self):
        """ Shouldn't be able to instantiate the interface """
        from pyramid_signup.interfaces import ISULoginSchema

        def make_session():
            ISULoginSchema('1')

        self.assertRaises(TypeError, make_session)

    def test_suloginform(self):
        """ Shouldn't be able to instantiate the interface """
        from pyramid_signup.interfaces import ISULoginForm

        def make_session():
            ISULoginForm('1')

        self.assertRaises(TypeError, make_session)
