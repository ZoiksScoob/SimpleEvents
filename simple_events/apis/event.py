import logging
import uuid
from flask_restx import Namespace, Resource, fields

from simple_events.models import db
from simple_events.models.auth import User
from simple_events.models.event import Event, Ticket
from simple_events.apis.auth import token_parser, status_message_model


# Get logger
logger = logging.getLogger(__name__)

# Namespace
api = Namespace('event', description='All Things Event Related')


# Custom types
def natural_num_type(value):
    if isinstance(value, int) and value >= 1:
        return value
    raise ValueError('initial_number_of_tickets must be an integer >= 1.')

natural_num_type.__schema__ = {'type': 'integer', 'format': 'my-custom-natural-num'}

# Parser
create_event_parser = token_parser.copy()
create_event_parser.add_argument('name', required=True, location='json')
create_event_parser.add_argument(
    'initial_number_of_tickets',
    type=natural_num_type,
    required=True,
    location='json')

event_status_parser = token_parser.copy()

event_download_parser = token_parser.copy()

event_add_parser = token_parser.copy()
event_add_parser.add_argument(
    'additionalNumberOfTickets',
    type=natural_num_type,
    required=True,
    location='json')

# Models
event_create_model = api.inherit('EventCreateData', status_message_model, {
    'eventIdentifier': fields.String(
        required=True,
        description='The unique identifier of the event.')
})

status_data_model = api.model('EventStatusData', {
    'name': fields.String(required=True, description='Name of the event.'),
    'number_of_tickets': fields.Integer(
        required=True,
        description='The total number of tickets of the event.'),
    'number_of_redeemed_tickets': fields.Integer(
        required=True,
        description='The number of redeemed tickets of the event.')
})

event_status_model = api.inherit('StatusDataModel', status_message_model, {
    'data': fields.Nested(status_data_model, required=True)
})

download_data_model = api.model('EventDowloadData', {
    'eventIdentifiers': fields.List(
        fields.String(required=True, description='ticketIdentifier.'),
        required=True,
        description='List of ticketIdentifiers.'
        )}
    )

event_dowload_model = api.inherit('EventDowloadModel', status_message_model, {
    'data': fields.Nested(download_data_model, required=True)
})


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
    @api.marshal_with(event_create_model)
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
                    'message': f'Successfully created event "{event.name}".',
                    'eventIdentifier': str(uuid.UUID(bytes=event.guid))
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


@api.route('/status/<uuid:eventIdentifier>')
@api.expect(event_status_parser)
class Status(Resource):
    """
    Event Status Resource
    """
    @api.doc(responses={
        200: 'Successfully retrieved event status.',
        400: 'Bad Request',
        401: 'The token is blacklisted, invalid, or the signature expired.',
        500: 'An Internal Server Error Occurred.'
    })
    @api.marshal_with(event_status_model)
    def get(self, eventIdentifier):
        """Get status of an event"""
        params = event_status_parser.parse_args()

        try:
            resp = User.decode_auth_token(params['Authorization'])

            if not isinstance(resp, str):

                result = db.session.query(
                            Event.name.label('name'),
                            db.func.count(Ticket.id).label('total'),
                            db.func.sum(Ticket.is_redeemed).label('redeemed')
                        )\
                        .join(Event)\
                        .filter(Event.guid == eventIdentifier.bytes)\
                        .group_by(Event.name)\
                        .first()

                response_object = {
                    'status': 'success',
                    'message': 'Successfully retrieved event status.',
                    'data': {
                        'name': result.name,
                        'number_of_tickets': result.total,
                        'number_of_redeemed_tickets': int(result.redeemed)
                    }}
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


@api.route('/download/<uuid:eventIdentifier>')
@api.expect(event_download_parser)
class Download(Resource):
    """
    Event Download Resource
    """
    @api.doc(responses={
        200: 'Successfully downloaded unredeemed event tickets.',
        400: 'Bad Request',
        401: 'The token is blacklisted, invalid, or the signature expired.',
        402: 'Invalid eventIdentifier.',
        500: 'An Internal Server Error Occurred.'
    })
    @api.marshal_with(event_dowload_model)
    def get(self, eventIdentifier):
        """Get download of an events unreemed tickets"""
        params = event_download_parser.parse_args()

        try:
            resp = User.decode_auth_token(params['Authorization'])

            if not isinstance(resp, str):

                event = Event.query.filter_by(guid=eventIdentifier.bytes).first()

                if not event:
                    response_object = {
                        'status': 'fail',
                        'message': 'Invalid eventIdentifier.'
                        }
                    return response_object, 402

                result = db.session.query(
                            Ticket.guid.label('guid')
                        )\
                    .filter(db.and_(
                        Ticket.event_id == event.id,
                        Ticket.is_redeemed == False # Doesn't select if "is" is used instead of "=="
                    ))\
                    .all()

                ticket_identifiers = [str(uuid.UUID(bytes=row.guid)) for row in result]

                response_object = {
                    'status': 'success',
                    'message': 'Successfully downloaded unredeemed event tickets.',
                    'data': {
                        'eventIdentifiers': ticket_identifiers
                    }}
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


@api.route('/add/<uuid:eventIdentifier>')
@api.expect(event_add_parser)
class Add(Resource):
    """
    Event Add Resource
    """
    @api.doc(responses={
        200: 'Successfully added tickets to event.',
        400: 'Bad Request',
        401: 'The token is blacklisted, invalid, or the signature expired.',
        402: 'Invalid eventIdentifier.',
        500: 'An Internal Server Error Occurred.'
    })
    def put(self, eventIdentifier):
        """Add more tickets to an existing event"""
        params = event_add_parser.parse_args()

        try:
            resp = User.decode_auth_token(params['Authorization'])

            if not isinstance(resp, str):
                event = Event.query.filter_by(guid=eventIdentifier.bytes).first()

                if not event:
                    response_object = {
                        'status': 'fail',
                        'message': 'Invalid eventIdentifier.'
                        }
                    return response_object, 402

                if event.additional_number_of_tickets:
                    event.additional_number_of_tickets += params['additionalNumberOfTickets']
                else:
                    event.additional_number_of_tickets = params['additionalNumberOfTickets']

                tickets = (Ticket(author_id=resp, event_id=event.id)
                           for _ in range(params['additionalNumberOfTickets']))

                db.session.add_all(tickets)
                db.session.commit()

                response_object = {
                    'status': 'success',
                    'message': f'Successfully added {params["additionalNumberOfTickets"]} event tickets.',
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
