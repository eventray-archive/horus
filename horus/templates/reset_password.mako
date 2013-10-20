<html>
  <body>
    ${render_flash_messages()|n}
    <h1>Reset Password</h1>
    ${form|n}
    <p>Don't have an account? <a href="${request.route_url('register')}">Sign up!</a></p>
  </body>
</html>

