from simple_events.models.db import db, bcrypt
from simple_events.models.auth import User, BlacklistToken
from simple_events.models.event import Event, Ticket

# Imports into here so that imports of all the models are made
# before db is imported into app.py and migration initialised.