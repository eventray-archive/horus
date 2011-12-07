class TestViews(UnitTestBase):
    def test_login_loads(self):
        request = testing.DummyRequest()
        request.user = None
        view = LoginView(request)
        response = view.get()

        assert response.get('form', None)
