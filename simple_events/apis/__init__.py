from flask_restx import Api

from simple_events.apis.auth import api as ns_auth
from simple_events.apis.event import api as ns_event
from simple_events.apis.ticket import api as ns_ticket


api = Api(
    title='Simple Events API',
    version='1.0',
    description='An API for a simple Events & Tickets management.'
)

# Add namespaces
api.add_namespace(ns_auth)
api.add_namespace(ns_event)
api.add_namespace(ns_ticket)
