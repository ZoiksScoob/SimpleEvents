import json
from flask_testing import TestCase

from simple_events.app import app
from simple_events.models import db


class BaseTestCase(TestCase):
    """ Base Tests """

    def create_app(self):
        app.config.from_object('simple_events.config.TestingConfig')
        return app

    def setUp(self):
        db.create_all()
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def register_user(self, username, password):
        return self.client.post(
            'auth/register',
            data=json.dumps(dict(
                username=username,
                password=password
            )),
            content_type='application/json',
        )

    def login_user(self, username, password):
        return self.client.post(
            'auth/login',
            data=json.dumps(dict(
                username=username,
                password=password
            )),
            content_type='application/json',
        )
