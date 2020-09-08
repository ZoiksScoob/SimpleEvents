import logging
from flask_restx import Namespace, Resource, fields, reqparse

from simple_events.models.db import db, bcrypt
from simple_events.models.auth import User, BlacklistToken

# Get logger
logger = logging.getLogger(__name__)

# Namespace
api = Namespace('auth', description='User Authentication & Tokens')

# Parsers
usr_pwd_parser = reqparse.RequestParser(bundle_errors=True)
usr_pwd_parser.add_argument('username', required=True, location='json')
usr_pwd_parser.add_argument('password', required=True, location='json')

token_parser = reqparse.RequestParser()
token_parser.add_argument('Authorization', required=True, location='headers')

# Models
status_message_model = api.model('StatusMessage', {
    'status': fields.String(
        required=True,
        description='Status of the request.',
        enum=['success', 'fail']),
    'message': fields.String(
        required=True,
        description='Message from the server giving more detail on the status of the request.'
        )
})

status_message_token_model = api.inherit('StatusMessageToken', status_message_model, {
    'auth_token': fields.String(
        required=False,
        description='A signed authorisation token.'
        )
})

data_fields = api.model('UserInfo', {
    'username': fields.String(
        required=True, 
        description='Username.'),
    'registered_on': fields.DateTime(
        required=True,
        description='Date & time of when the user was registered.'
    )
})

status_message_data_model = api.inherit('StatusMessageData', status_message_model, {
    'data': fields.Nested(data_fields)
})


@api.route('/register')
@api.expect(usr_pwd_parser)
class Register(Resource):
    """
    User Registration Resource
    """
    @api.doc(responses={
        200: 'Successfully registered.',
        201: 'User already exists. Please Log in.',
        400: 'Bad Request',
        500: 'An Internal Server Error Occurred.'
    })
    @api.marshal_with(status_message_token_model)
    def post(self):
        post_data = usr_pwd_parser.parse_args()

        try:
            # check if user already exists
            user = User.query.filter_by(
                username=post_data['username']).first()

            if not user:
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
                return response_object, 200

            else:
                response_object = {
                    'status': 'fail',
                    'message': 'User already exists. Please Log in.',
                }
                return response_object, 201

        except Exception:
            logger.error('An error occurred registering a user', exc_info=True)

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
    @api.doc(responses={
        200: 'Successfully logged in.',
        400: 'Bad Request',
        404: 'User does not exist.',
        500: 'An Internal Server Error Occurred.'
    })
    @api.marshal_with(status_message_token_model)
    def post(self):
        # get the post data
        post_data = usr_pwd_parser.parse_args()

        try:
            # fetch the user data
            user = User.query.filter_by(username=post_data['username']).first()

            if user and bcrypt.check_password_hash(
                pw_hash=user.password, password=post_data['password']
            ):
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

        except Exception:
            logger.error('An error occurred logging in a user', exc_info=True)

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
    @api.doc(responses={
        200: 'Successfully logged in.',
        400: 'Bad Request',
        401: 'The token is blacklisted, invalid, or the signature expired.',
        500: 'An Internal Server Error Occurred.'
    })
    @api.marshal_with(status_message_data_model)
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
                        'registered_on': user.registered_on
                    }
                }
                return response_object, 200

            response_object = {
                'status': 'fail',
                'message': resp
            }
            return response_object, 401

        except Exception:
            logger.error('An error occurred checking status of a user', exc_info=True)

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
    @api.doc(responses={
        200: 'Successfully logged out.',
        400: 'Bad Request',
        401: 'The token is already blacklisted, invalid, or the signature expired.',
        500: 'An Internal Server Error Occurred.'
    })
    @api.marshal_with(status_message_model)
    def post(self):
        # get auth token
        auth_header = token_parser.parse_args()
        auth_token = auth_header['Authorization']

        try:
            resp = User.decode_auth_token(auth_token)

            if not isinstance(resp, str):
                # mark the token as blacklisted
                blacklist_token = BlacklistToken(token=auth_token)

                # insert the token
                db.session.add(blacklist_token)
                db.session.commit()

                response_object = {
                    'status': 'success',
                    'message': 'Successfully logged out.'
                }
                return response_object, 200

            else:
                response_object = {
                    'status': 'fail',
                    'message': resp
                }
                return response_object, 401

        except Exception:
            logger.error('An error occurred logging in a user', exc_info=True)

            response_object = {
                'status': 'fail',
                'message': 'An Internal Server Error Occurred.'
            }
            return response_object, 500
