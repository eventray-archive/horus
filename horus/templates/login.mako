<html>
  <body>
    <a href="${request.route_url('index')}">Back to index</a>
    ${render_flash_messages()|n}
    <h1>Login</h1>
    ${form|n}
    <p><a href="${request.route_url('forgot_password')}">Forgot your password?</a></p>
    <p>Don't have an account? <a href="${request.route_url('register')}">Sign up!</a></p>
  </body>
</html>
