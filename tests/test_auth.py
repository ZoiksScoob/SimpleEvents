import time
import json
import unittest

from simple_events.models import db
from simple_events.models.auth import User, BlacklistToken
from tests.base import BaseTestCase


class TestAuthBlueprint(BaseTestCase):

    def test_registration(self):
        """ Test for user registration """
        with self.client:
            response = self.register_user('dummy_username', '12345678')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Successfully registered.')
            self.assertTrue(data['auth_token'])
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 200)

    def test_registration_with_too_short_password(self):
        """ Test for user registration with too a short password """
        with self.client:
            response = self.register_user('dummy_username', '123456')
            data = json.loads(response.data.decode())
            self.assertTrue(data['message'] == "Input payload validation failed")
            self.assertTrue(data['errors'])
            self.assertTrue(data['errors']['password'] == "Password must be between 8 and 255 characters long.")
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 400)

    def test_registered_with_already_registered_user(self):
        """ Test registration with already registered username """
        user = User(
            username='dummy_username',
            password='test'
        )
        db.session.add(user)
        db.session.commit()
        with self.client:
            response = self.register_user('dummy_username', '12345678')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(
                data['message'] == 'User already exists. Please Log in.')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 201)

    def test_registered_user_login(self):
        """ Test for login of registered-user login """
        with self.client:
            # user registration
            resp_register = self.register_user('dummy_username', '12345678')
            data_register = json.loads(resp_register.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(
                data_register['message'] == 'Successfully registered.'
            )
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(resp_register.content_type == 'application/json')
            self.assertEqual(resp_register.status_code, 200)
            # registered user login
            response = self.login_user('dummy_username', '12345678')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Successfully logged in.')
            self.assertTrue(data['auth_token'])
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 200)

    def test_non_registered_user_login(self):
        """ Test for login of non-registered user """
        with self.client:
            response = self.login_user('dummy_username', '12345678')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'User does not exist.')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 404)

    def test_user_login_with_too_short_password(self):
        """ Test for login with too short a password """
        with self.client:
            # user registration
            resp_register = self.register_user('dummy_username', '12345678')
            data_register = json.loads(resp_register.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(
                data_register['message'] == 'Successfully registered.'
            )
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(resp_register.content_type == 'application/json')
            self.assertEqual(resp_register.status_code, 200)
            # invalid login
            response = self.login_user('dummy_username', '1234567')
            data = json.loads(response.data.decode())
            self.assertTrue(data['message'] == "Input payload validation failed")
            self.assertTrue(data['errors'])
            self.assertTrue(data['errors']['password'] == "Password must be between 8 and 255 characters long.")
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 400)

    def test_user_status(self):
        """ Test for user status """
        with self.client:
            resp_register = self.register_user('dummy_username', '12345678')
            response = self.client.get(
                '/auth/status',
                headers=dict(
                    Authorization=json.loads(
                        resp_register.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['data'] is not None)
            self.assertTrue(data['data']['username'] == 'dummy_username')
            self.assertEqual(response.status_code, 200)

    def test_user_status_invalid_token(self):
        """ Test for user status with malformed bearer token"""
        with self.client:
            resp_register = self.register_user('dummy_username', '12345678')
            response = self.client.get(
                '/auth/status',
                headers=dict(
                    Authorization='Some nonsense'
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Invalid token. Please log in again.')
            self.assertEqual(response.status_code, 401)

    def test_valid_logout(self):
        """ Test for logout before token expires """
        with self.client:
            # user registration
            resp_register = self.register_user('dummy_username', '12345678')
            data_register = json.loads(resp_register.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(
                data_register['message'] == 'Successfully registered.')
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(resp_register.content_type == 'application/json')
            self.assertEqual(resp_register.status_code, 200)
            # user login
            resp_login = self.login_user('dummy_username', '12345678')
            data_login = json.loads(resp_login.data.decode())
            self.assertTrue(data_login['status'] == 'success')
            self.assertTrue(data_login['message'] == 'Successfully logged in.')
            self.assertTrue(data_login['auth_token'])
            self.assertTrue(resp_login.content_type == 'application/json')
            self.assertEqual(resp_login.status_code, 200)
            # valid token logout
            response = self.client.post(
                '/auth/logout',
                headers=dict(
                    Authorization=json.loads(
                        resp_login.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Successfully logged out.')
            self.assertEqual(response.status_code, 200)

    def test_invalid_logout(self):
        """ Testing logout after the token expires """
        with self.client:
            # user registration
            resp_register = self.register_user('dummy_username', '12345678')
            data_register = json.loads(resp_register.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(
                data_register['message'] == 'Successfully registered.')
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(resp_register.content_type == 'application/json')
            self.assertEqual(resp_register.status_code, 200)
            # user login
            resp_login = self.login_user('dummy_username', '12345678')
            data_login = json.loads(resp_login.data.decode())
            self.assertTrue(data_login['status'] == 'success')
            self.assertTrue(data_login['message'] == 'Successfully logged in.')
            self.assertTrue(data_login['auth_token'])
            self.assertTrue(resp_login.content_type == 'application/json')
            self.assertEqual(resp_login.status_code, 200)
            # invalid token logout
            wait_time = self.client.application.config['AUTH_TOKEN_EXPIRY_SECONDS']
            time.sleep(wait_time + 5)
            response = self.client.post(
                '/auth/logout',
                headers=dict(
                    Authorization=json.loads(
                        resp_login.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(
                data['message'] == 'Signature expired. Please log in again.')
            self.assertEqual(response.status_code, 401)

    def test_valid_blacklisted_token_logout(self):
        """ Test for logout after a valid token gets blacklisted """
        with self.client:
            # user registration
            resp_register = self.register_user('dummy_username', '12345678')
            data_register = json.loads(resp_register.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(
                data_register['message'] == 'Successfully registered.')
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(resp_register.content_type == 'application/json')
            self.assertEqual(resp_register.status_code, 200)
            # user login
            resp_login = self.login_user('dummy_username', '12345678')
            data_login = json.loads(resp_login.data.decode())
            self.assertTrue(data_login['status'] == 'success')
            self.assertTrue(data_login['message'] == 'Successfully logged in.')
            self.assertTrue(data_login['auth_token'])
            self.assertTrue(resp_login.content_type == 'application/json')
            self.assertEqual(resp_login.status_code, 200)
            # blacklist a valid token
            blacklist_token = BlacklistToken(
                token=json.loads(resp_login.data.decode())['auth_token'])
            db.session.add(blacklist_token)
            db.session.commit()
            # blacklisted valid token logout
            response = self.client.post(
                '/auth/logout',
                headers=dict(
                    Authorization=json.loads(
                        resp_login.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Token blacklisted. Please log in again.')
            self.assertEqual(response.status_code, 401)

    def test_valid_blacklisted_token_user(self):
        """ Test for user status with a blacklisted valid token """
        with self.client:
            resp_register = self.register_user('dummy_username', '12345678')
            # blacklist a valid token
            blacklist_token = BlacklistToken(
                token=json.loads(resp_register.data.decode())['auth_token'])
            db.session.add(blacklist_token)
            db.session.commit()
            response = self.client.get(
                '/auth/status',
                headers=dict(
                    Authorization=json.loads(
                        resp_register.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Token blacklisted. Please log in again.')
            self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()
