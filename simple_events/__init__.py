import os
from flask import Flask
from flask_uuid import FlaskUUID


def create_app(app_name, test_config=None):
    # create and configure the app
    app = Flask(app_name, instance_relative_config=True)
    
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'simple_events.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialise UUID extension
    FlaskUUID(app)

    # Setup database
    from . import db
    db.init_app(app)

    # Register blueprints
    from . import auth, event
    app.register_blueprint(auth.bp)

    app.register_blueprint(event.bp)
    app.add_url_rule('/', endpoint='index')

    return app
