import logging
from flask_restx import Namespace, Resource, fields, reqparse

from simple_events.models import db
from simple_events.models.auth import User
from simple_events.models.event import Event, Ticket
from simple_events.apis.auth import token_parser


# Get logger
logger = logging.getLogger(__name__)

# Namespace
api = Namespace('event', description='All Things Event Related')


@api.route('/create')
class Create(Resource):
    """
    Event Create Resource
    """
    def post(self):
        """Create an event"""
        pass


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
