import os
from flask import Flask
from flask_uuid import FlaskUUID
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS


app = Flask(__name__, instance_relative_config=True)

# Initialise Cross-Origin Resource Sharing extension
CORS(app)

app_settings = os.getenv(
    'APP_SETTINGS',
    'simple_events.config.DevelopmentConfig'
)

app.config.from_object(app_settings)

# Initialise UUID extension
FlaskUUID(app)

# Instantiate bcrypt hashing utilities
bcrypt = Bcrypt(app)

# Instantiate database
db = SQLAlchemy(app)

# Register blueprints
# Import here to avoid circular import issue
from simple_events.views import auth

app.register_blueprint(auth.auth_blueprint)
