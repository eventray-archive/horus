<html>
  <body>
    <a href="${request.route_url('index')}">Back to Index</a>
    ${render_flash_messages()|n}
    <h1>Profile</h1>
    ${ user.username }<br />
    ${ user.email }
  </body>
</html>
