from flask_restx import Api, Namespace

from simple_events.apis.auth import api as ns_auth


api = Api(
    title='Simple Events API',
    version='1.0',
    description='An API for a simple Events & Tickets management.'
)

# Add namespaces
api.add_namespace(ns_auth)
