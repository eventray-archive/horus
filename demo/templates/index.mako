<html>
  <body>
    % for type in ['success', 'error', 'warning', 'info']:
      % if request.session.peek_flash(type):
        % for message in request.session.pop_flash(type):
          <div class="alert-message ${type}">
            <p><strong>${message}</strong></p>
          </div>
        % endfor
      % endif
    % endfor
    % if request.user:
      Welcome, <a href="${request.route_url('profile', user_pk=request.user.pk)}">${request.user.display_name}</a>
      <a href="${request.route_url('logout')}">Logout</a>
    % else:
      <a href="${request.route_url('login')}">Login</a>
      <a href="${request.route_url('register')}">Register</a>
    % endif
  </body>
</html>
