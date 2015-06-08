kaizen
===============

This is a web framework based on the 'flask' python web microframework.

http://flask.pocoo.org/

It's currently based on top of Flask-Classy.

https://pythonhosted.org/Flask-Classy/

We expect the RethinkDB Database version 2.X or above to be installed.

http://www.rethinkdb.com/

The RethinkDB Python driver is also required.

This system is based on many modules. 

It comes as an example website which can be customized to your use-case.

Here is a uwsgi config that might work.
```
[uwsgi]
# Variables          
socket = /var/run/uwsgi/net_mydomain_mysite.sock
sitename = mysite.mydomain.net
base = /var/www/sites/%(sitename)/private
home = %(base)/venv
pythonpath = %(base)
module = run
callable = flask_core
logto = %(base)/../log/uwsgi.log
procname-prefix = %(sitename)-
```

Here is an nginx config that might work.
```
# UWSGI proxy_pass for nginx

server {
	listen                  [::]:80; # Both IPv4 and IPv6 (HTTP)

	server_name	mysite.mydomain.net;
	access_log	/var/www/sites/mysite.mydomain.net/log/access.log;
	error_log	/var/www/sites/mysite.mydomain.net/log/error.log;

	location /static { alias /var/www/sites/mysite.mydomain.net/private/app/static/; }
	location / { try_files $uri @app; }
	location @app {
		include uwsgi_params;
		uwsgi_pass unix:/var/run/uwsgi/net_mydomain_mysite.sock;
		}
	}

```