<%inherit file="horus:templates/layout.mako"/>

% for user in users:
  ${user.user_name} [<a href="${request.route_url('horus_admin_users_edit', user_id=user.id)}">Edit</a>]
% endfor
