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
    guid = db.Column(db.BLOB, nullable=False, default=uuid.uuid4)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date_created_utc = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) 

    db.UniqueConstraint(guid, name='uix__event__guid')


class Ticket(db.Model):
    __tablename__ = "ticket"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    guid = db.Column(db.BLOB, nullable=False, default=uuid.uuid4)
    is_redeemed = db.Column(db.Boolean, default=False)
    date_created_utc = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    db.UniqueConstraint('guid', name='uix__ticket__guid')
