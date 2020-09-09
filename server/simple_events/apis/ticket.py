import logging
from flask_restx import Namespace, Resource

from simple_events.models import db
from simple_events.models.auth import User
from simple_events.models.event import Ticket
from simple_events.apis.auth import status_message_model, token_parser


# Get logger
logger = logging.getLogger(__name__)

# Namespace
api = Namespace('', description='All Things Ticket Related')


@api.route('/redeem/<uuid:ticketIdentifier>')
class Redeem(Resource):
    """
    Ticket Redeem Resource
    """
    @api.doc(responses={
        200: 'Ok',
        400: 'Bad Request',
        402: 'Invalid ticketIdentifier.',
        410: 'Gone: ticket redeemed',
        500: 'An Internal Server Error Occurred.'
    })
    @api.marshal_with(status_message_model)
    def get(self, ticketIdentifier):
        """Redeem a ticket"""
        try:
            ticket = Ticket.query.filter_by(guid=ticketIdentifier.bytes).first()

            if not ticket:
                response_object = {
                    'status': 'fail',
                    'message': 'Invalid ticketIdentifier.'
                    }
                return response_object, 402

            if ticket.is_redeemed:
                response_object = {
                    'status': 'success',
                    'message': 'GONE: ticket has already been redeemed.'
                }
                return response_object, 410

            ticket.is_redeemed = True

            db.session.commit()

            response_object = {
                    'status': 'success',
                    'message': 'OK: ticket redeemed.'
                }
            return response_object

        except Exception:
            logger.error('An error occurred creating an event.', exc_info=True)

            response_object = {
                'status': 'fail',
                'message': 'An Internal Server Error Occurred.',
            }
            return response_object, 500


@api.route('/status/<uuid:ticketIdentifier>')
@api.expect(token_parser)
class Status(Resource):
    """
    Ticket Status Resource
    """
    @api.doc(responses={
        200: 'Ok',
        400: 'Bad Request',
        401: 'The token is blacklisted, invalid, or the signature expired.',
        402: 'Invalid ticketIdentifier.',
        410: 'Gone: ticket redeemed',
        500: 'An Internal Server Error Occurred.'
    })
    @api.marshal_with(status_message_model)
    def get(self, ticketIdentifier):
        """Check status of ticket"""
        params = token_parser.parse_args()

        try:
            resp = User.decode_auth_token(params['Authorization'])

            if not isinstance(resp, str):
                ticket = Ticket.query.filter_by(guid=ticketIdentifier.bytes).first()

                if not ticket:
                    response_object = {
                        'status': 'fail',
                        'message': 'Invalid ticketIdentifier.'
                        }
                    return response_object, 402

                if ticket.is_redeemed:
                    response_object = {
                        'status': 'success',
                        'message': 'GONE: ticket redeemed.'
                    }
                    return response_object, 410

                response_object = {
                        'status': 'success',
                        'message': 'OK.'
                    }
                return response_object, 200

            response_object = {
                'status': 'fail',
                'message': resp
                }
            return response_object, 401

        except Exception:
            logger.error('An error occurred creating an event.', exc_info=True)

            response_object = {
                'status': 'fail',
                'message': 'An Internal Server Error Occurred.',
            }
            return response_object, 500
