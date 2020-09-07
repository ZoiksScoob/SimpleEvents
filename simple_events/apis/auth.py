from flask import request, make_response, jsonify
from flask_restx import Namespace, Resource, reqparse

from simple_events.models.db import db, bcrypt
from simple_events.models.auth import User, BlacklistToken

# Namespace
api = Namespace('auth', description='User Authentication & Tokens')

# Models
usr_pwd_parser = reqparse.RequestParser(bundle_errors=True)
usr_pwd_parser.add_argument('username', required=True, location='json')
usr_pwd_parser.add_argument('password', required=True, location='json')

token_parser = reqparse.RequestParser()
token_parser.add_argument('Authorization', required=True, location='headers')


@api.route('/register')
@api.expect(usr_pwd_parser)
class Register(Resource):
    """
    User Registration Resource
    """
    def post(self):
        post_data = usr_pwd_parser.parse_args()

        try:
            # check if user already exists
            user = User.query.filter_by(
                username=post_data['username']).first()

            if not user:
                try:
                    user = User(
                        username=post_data['username'],
                        password=post_data['password']
                    )

                    # insert the user
                    db.session.add(user)
                    db.session.commit()

                    # generate the auth token
                    auth_token = user.encode_auth_token(user.id)

                    response_object = {
                        'status': 'success',
                        'message': 'Successfully registered.',
                        'auth_token': auth_token.decode()
                    }
                    return response_object, 201

                except Exception as e:
                    response_object = {
                        'status': 'fail',
                        'message': 'Some error occurred. Please try again.'
                    }
                    return response_object, 501

            else:
                response_object = {
                    'status': 'fail',
                    'message': 'User already exists. Please Log in.',
                }
                return response_object, 202

        except:
            response_object = {
                'status': 'fail',
                'message': 'An Internal Server Error Occurred.',
            }
            return response_object, 500


@api.route('/login')
@api.expect(usr_pwd_parser)
class Login(Resource):
    """
    User Login Resource
    """
    def post(self):
        # get the post data
        post_data = usr_pwd_parser.parse_args()

        try:
            # fetch the user data
            user = User.query.filter_by(username=post_data['username']).first()

            passwords_match = bcrypt.check_password_hash(
                pw_hash=user.password, password=post_data['password']
            )

            if user and passwords_match:
                auth_token = user.encode_auth_token(user.id)

                if auth_token:
                    response_object = {
                        'status': 'success',
                        'message': 'Successfully logged in.',
                        'auth_token': auth_token.decode()
                    }
                    return response_object, 200

            else:
                response_object = {
                    'status': 'fail',
                    'message': 'User does not exist.'
                }
                return response_object, 404

        except Exception as e:
            response_object = {
                'status': 'fail',
                'message': 'An Internal Server Error Occurred.'
            }

            return response_object, 500


@api.route('/status')
@api.expect(token_parser)
class Status(Resource):
    """
    User Status Resource
    """
    def get(self):
        # get the auth token
        auth_header = token_parser.parse_args()
        auth_token = auth_header['Authorization']

        try:
            resp = User.decode_auth_token(auth_token)

            if not isinstance(resp, str):
                user = User.query.filter_by(id=resp).first()

                response_object = {
                    'status': 'success',
                    'data': {
                        'username': user.username,
                        'registered_on': user.registered_on.isoformat()
                    }
                }
                return response_object, 200

            response_object = {
                'status': 'fail',
                'message': resp
            }
            return response_object, 401

        except Exception as e:
            response_object = {
                'status': 'fail',
                'message': 'An Internal Server Error Occurred.'
            }
            return response_object, 500


@api.route('/logout')
@api.expect(token_parser)
class Logout(Resource):
    """
    Logout Resource
    """
    def post(self):
        # get auth token
        auth_header = token_parser.parse_args()
        auth_token = auth_header['Authorization']

        try:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                # mark the token as blacklisted
                blacklist_token = BlacklistToken(token=auth_token)
                try:
                    # insert the token
                    db.session.add(blacklist_token)
                    db.session.commit()
                    response_object = {
                        'status': 'success',
                        'message': 'Successfully logged out.'
                    }
                    return make_response(jsonify(response_object)), 200
                except Exception as e:
                    response_object = {
                        'status': 'fail',
                        'message': e
                    }
                    return make_response(jsonify(response_object)), 200
            else:
                response_object = {
                    'status': 'fail',
                    'message': resp
                }
                return make_response(jsonify(response_object)), 401

        except Exception as e:
            response_object = {
                'status': 'fail',
                'message': 'An Internal Server Error Occurred.'
            }
            return response_object, 500
