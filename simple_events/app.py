from flask import Flask
from flask_uuid import FlaskUUID
# from werkzeug.contrib.fixers import ProxyFix

from simple_events.apis import api
from simple_events.models.db import db
from simple_events.utils.helpers import get_app_settings


app = Flask(__name__, instance_relative_config=True)
# app.wsgi_app = ProxyFix(app.wsgi_app)

# Get settings
app_settings = get_app_settings()

app.config.from_object(app_settings)

# Initialise UUID extension
FlaskUUID(app)

# Initialise DB
db.init_app(app)

# Initialise API
api.init_app(app)

if __name__ == '__main__':
    app.run(debug=True)
