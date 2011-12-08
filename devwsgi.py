from paste.deploy import loadapp

app = loadapp('config:test.ini', relative_to='.')
