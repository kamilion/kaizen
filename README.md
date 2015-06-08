kaizen
===============

This is a web framework based on the 'flask' python web microframework.
Several additional contrib modules are in use, such as Flask-Login, Flask-WTF, and Flask-UUID.

http://flask.pocoo.org/

It's currently based on top of Flask-Classy. URL Routing is handled from here. 
Each class gets it's own imports and need not share with the rest of the application.

https://pythonhosted.org/Flask-Classy/

We use the Remodel ORM by @linkyndy to access RethinkDB's JSON store. Treat it like Peewee.

https://github.com/linkyndy/remodel

We expect the RethinkDB Database version 2.X or above and it's python driver to be installed.

http://www.rethinkdb.com/

Here is some useful documentation on working with remodel circa 0.4.2:

http://www.rethinkdb.com/blog/remodel/

https://github.com/linkyndy/remodel/wiki/Models

https://github.com/linkyndy/remodel/wiki/Callbacks



This system is based on many plugin modules.
By default, the initializer in the app subdirectory will look for a templates folder in each top level directory.
Please do the smart thing and create a subdirectory within the templates folder containing the plugin-specific templates.

Kaizen comes as an example website which can be customized to your use-case.
It is fully functional and serves as an example of an integrated, running website.

The core of kaizen is within the 'app' subdirectory.
Within it is the main configuration file, a python importable series of dicts.
Also of note is the ```app/__init__.py``` which is currently where the site administrator must register views.

Here is an example of how new views are registered with the flask_core.

```python
# PagesView imports
from pages.pagesview import PagesView

# TicketsView imports
from tickets.ticketsview import TicketsView

# PagesView registration
PagesView.register(flask_core)

# TicketsView registration
TicketsView.register(flask_core)
```

It is useful to note that only the view must be registered.
In this way, you may make use of one or more models or forms without altering the kaizen core.
It is recommended that you do not remove the baseplate view, but modify it as needed, along with it's templates.
In the future, we may look at improving the core to seek out plugins in a more effective manner.

There is currently no defined hard dependancies between plugins.
Some of the core plugins may be harder to purge from your project than others.
Core plugins that will likely cause you grief if removed:
app, auth, maybe billing.stripe if too many other plugins begin to rely on it.

Windows:
Last major problem was ```pyotp```, which was removed.
Good luck finding a wheel for ```scrypt```. If you can, everything'll probably work. You're on your own though.
If you DO find a good ```scrypt``` wheel for windows, let @kamilion know, eh?

Linux/OSX/Unixy-OSs:
For debugging purpouses, setting a virtualenv up and executing the run.sh script should work.

First time:

```shell
virtualenv venv
source venv/bin/activate
pip install --upgrade pip setuputils
pip install -r requirements.txt
./run.py
```

Recurring development using the default 'venv' name:

```shell
./run.sh
```


For production, Here is a uwsgi config that might work.

```INI
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

Here is an nginx config that might work with the above uwsgi config.

```Nginx
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

@kamilion can be found using the ZNC logging proxy on Freenode IRC under the nickname Kamilion.
Find him in one of 80 popular linux-related channels, or leave a message and maybe he'll get back to you.
You'll probably find him here: http://webchat.freenode.net/?channels=kamikazi

If you break kaizen, you get to keep both pieces.
However, we will accept photocopies of broken pieces, stuff them in the github issuebox.
(if you have no sense of humor, that means post your tracebacks on the github issue tracker.)