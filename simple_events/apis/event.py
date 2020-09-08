import logging
from flask_restx import Namespace, Resource, fields, reqparse

from simple_events.models import db
from simple_events.models.auth import User
from simple_events.models.event import Event, Ticket
from simple_events.apis.auth import token_parser, status_message_model


# Get logger
logger = logging.getLogger(__name__)

# Namespace
api = Namespace('event', description='All Things Event Related')


# Custom types
def ticket_int_type(value):
    if isinstance(value, int) and value >= 1:
        return value
    raise ValueError('initial_number_of_tickets must be an integer >= 1.')

ticket_int_type.__schema__ = {'type': 'integer', 'format': 'my-custom-ticket-int'}

# Parser
create_event_parser = token_parser.copy()
create_event_parser.add_argument('name', required=True, location='json')
create_event_parser.add_argument('initial_number_of_tickets', type=ticket_int_type, required=True, location='json')


@api.route('/create')
@api.expect(create_event_parser)
class Create(Resource):
    """
    Event Create Resource
    """
    @api.doc(responses={
        200: 'Successfully created event.',
        400: 'Bad Request',
        401: 'The token is blacklisted, invalid, or the signature expired.',
        500: 'An Internal Server Error Occurred.'
    })
    @api.marshal_with(status_message_model)
    def post(self):
        """Create an event"""
        post_data = create_event_parser.parse_args()

        try:
            resp = User.decode_auth_token(post_data['Authorization'])

            if not isinstance(resp, str):
                event = Event(
                    name=post_data['name'],
                    initial_number_of_tickets=post_data['initial_number_of_tickets'],
                    author_id=resp
                )

                db.session.add(event)
                db.session.flush()

                tickets = (Ticket(author_id=resp, event_id=event.id)
                           for _ in range(post_data['initial_number_of_tickets']))

                db.session.add_all(tickets)
                db.session.commit()

                response_object = {
                    'status': 'success',
                    'message': f'Successfully created event "{event.name}".'
                    }
                return response_object, 200

            response_object = {
                'status': 'fail',
                'message': resp
                }
            return response_object, 401

        except Exception:
            logger.error('An error occurred registering a user', exc_info=True)

            response_object = {
                'status': 'fail',
                'message': 'An Internal Server Error Occurred.',
            }
            return response_object, 500


@api.route('/<uuid:eventIdentifier>/status')
class Status(Resource):
    """
    Event Status Resource
    """
    def get(self, eventIdentifier):
        """Get status of an event"""
        pass


@api.route('/<uuid:eventIdentifier>/download')
class Download(Resource):
    """
    Event Download Resource
    """
    def get(self, eventIdentifier):
        """Get download of an events unreemed tickets"""
        pass


@api.route('/add')
class Download(Resource):
    """
    Event Download Resource
    """
    def put(self, eventIdentifier):
        """Add more tickets to an existing event"""
        pass
