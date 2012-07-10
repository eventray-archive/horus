<%inherit file="hiero:templates/layout.mako"/>

% if appstruct:
  ${form.render(appstruct=appstruct)|n}
% else:
  ${form.render()|n}
% endif
