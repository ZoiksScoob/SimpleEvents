import uuid
from datetime import datetime
from simple_events.models.db import db


class Event(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "event"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    initial_number_of_tickets = db.Column(db.Integer, nullable=False)
    additional_number_of_tickets = db.Column(db.Integer, nullable=True)
    guid = db.Column(db.BLOB, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date_created_utc = db.Column(db.DateTime, nullable=False)

    db.UniqueConstraint(guid, name='uix__event__guid')

    def __init__(self, name, initial_number_of_tickets, author_id):
        self.name = name
        self.initial_number_of_tickets = initial_number_of_tickets
        self.author_id = author_id
        self.guid = uuid.uuid4().bytes
        self.date_created_utc = datetime.utcnow()


class Ticket(db.Model):
    __tablename__ = "ticket"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    guid = db.Column(db.BLOB, nullable=False)
    is_redeemed = db.Column(db.Boolean)
    date_created_utc = db.Column(db.DateTime, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    db.UniqueConstraint('guid', name='uix__ticket__guid')

    def __init__(self, event_id, author_id):
        self.event_id = event_id
        self.guid = uuid.uuid4().bytes
        self.is_redeemed = False
        self.date_created_utc = datetime.utcnow()
        self.author_id = author_id
