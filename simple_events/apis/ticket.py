import logging
from flask_restx import Namespace, Resource

from simple_events.models import db
from simple_events.models.auth import User
from simple_events.models.event import Ticket
from simple_events.apis.auth import status_message_model


# Get logger
logger = logging.getLogger(__name__)

# Namespace
api = Namespace('', description='All Things Event Related')


@api.route('/redeem/<uuid:ticketIdentifier>')
class Create(Resource):
    """
    Event Create Resource
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
                    'status': 'fail',
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
