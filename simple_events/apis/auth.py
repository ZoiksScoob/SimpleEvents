from flask import request, make_response, jsonify
from flask_restx import Namespace, Resource, reqparse

from simple_events.models.db import db, bcrypt
from simple_events.models.auth import User, BlacklistToken

# Namespace
api = Namespace('auth', description='User Authentication & Tokens')

# Models
usr_pwd_parser = reqparse.RequestParser(bundle_errors=True)
usr_pwd_parser.add_argument('username', required=True)
usr_pwd_parser.add_argument('password', required=True)


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
            user = User.query.filter_by(username=post_data.get('username')).first()

            passwords_match = bcrypt.check_password_hash(
                pw_hash=user.password, password=post_data.get('password')
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
                'message': 'Try again'
            }

            return response_object, 500


@api.route('/status')
class Status(Resource):
    """
    User Status Resource
    """
    def get(self):
        # get the auth token
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                auth_token = auth_header.split(" ")[1]
            except IndexError:
                responseObject = {
                    'status': 'fail',
                    'message': 'Bearer token malformed.'
                }
                return make_response(jsonify(responseObject)), 401
        else:
            auth_token = ''
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                user = User.query.filter_by(id=resp).first()
                responseObject = {
                    'status': 'success',
                    'data': {
                        'user_id': user.id,
                        'username': user.username,
                        'registered_on': user.registered_on
                    }
                }
                return make_response(jsonify(responseObject)), 200
            responseObject = {
                'status': 'fail',
                'message': resp
            }
            return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return make_response(jsonify(responseObject)), 401


@api.route('/logout')
class Logout(Resource):
    """
    Logout Resource
    """
    def post(self):
        # get auth token
        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = ''
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                # mark the token as blacklisted
                blacklist_token = BlacklistToken(token=auth_token)
                try:
                    # insert the token
                    db.session.add(blacklist_token)
                    db.session.commit()
                    responseObject = {
                        'status': 'success',
                        'message': 'Successfully logged out.'
                    }
                    return make_response(jsonify(responseObject)), 200
                except Exception as e:
                    responseObject = {
                        'status': 'fail',
                        'message': e
                    }
                    return make_response(jsonify(responseObject)), 200
            else:
                responseObject = {
                    'status': 'fail',
                    'message': resp
                }
                return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return make_response(jsonify(responseObject)), 403
