from flask import request, make_response, jsonify
from flask_restx import Namespace, Resource, fields

from simple_events.models.db import db, bcrypt
from simple_events.models.auth import User, BlacklistToken

# Namespace
api = Namespace('auth', description='User Authentication & Tokens')

# Models
username_password_model = api.model('Register', {
    'username': fields.String(required=True),
    'password': fields.String(required=True),
})


@api.route('/register')
class Register(Resource):
    """
    User Registration Resource
    """

    @api.doc('register_user')
    @api.expect(username_password_model)
    def post(self):
        try:
            # get the post data
            post_data = request.json

            if not post_data:
                responseObject = {
                        'status': 'fail',
                        'message': "Unable to retrieve json payload. Please ensure header {'Content-Type': 'application/json'} is included in your request."
                    }
                return responseObject, 401

            # check if user already exists
            user = User.query.filter_by(
                username=post_data.get('username')).first()

            if not user:
                try:
                    user = User(
                        username=post_data.get('username'),
                        password=post_data.get('password')
                    )
                    # insert the user
                    db.session.add(user)
                    db.session.commit()
                    # generate the auth token
                    auth_token = user.encode_auth_token(user.id)
                    responseObject = {
                        'status': 'success',
                        'message': 'Successfully registered.',
                        'auth_token': auth_token.decode()
                    }
                    return responseObject, 201
                except Exception as e:
                    responseObject = {
                        'status': 'fail',
                        'message': 'Some error occurred. Please try again.'
                    }
                    return responseObject, 501
            else:
                responseObject = {
                    'status': 'fail',
                    'message': 'User already exists. Please Log in.',
                }
                return responseObject, 202
        except:
            responseObject = {
                'status': 'fail',
                'message': 'An Internal Server Error Occurred.',
            }
            return responseObject, 500



@api.route('/login')
class Login(Resource):
    """
    User Login Resource
    """
    @api.doc('login_user')
    @api.expect(username_password_model)
    @api.marshal_with(username_password_model, code=201)
    def post(self):
        # get the post data
        post_data = api.payload
        try:
            # fetch the user data
            user = User.query.filter_by(
                username=post_data.get('username')
            ).first()
            if user and bcrypt.check_password_hash(
                post_data.get('password'), user.password
            ):
                auth_token = user.encode_auth_token(user.id)
                if auth_token:
                    responseObject = {
                        'status': 'success',
                        'message': 'Successfully logged in.',
                        'auth_token': auth_token.decode()
                    }
                    return make_response(jsonify(responseObject)), 200
            else:
                responseObject = {
                    'status': 'fail',
                    'message': 'User does not exist.'
                }
                return make_response(jsonify(responseObject)), 404
        except Exception as e:
            print(e)
            responseObject = {
                'status': 'fail',
                'message': 'Try again'
            }
            return make_response(jsonify(responseObject)), 500


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
