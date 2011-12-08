from paste.deploy import loadapp

app = loadapp('config:demo.ini', relative_to='.')
