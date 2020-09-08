import unittest
import uuid
import time
from datetime import datetime

from simple_events.models import db
from simple_events.models.event import Event, Ticket
from simple_events.models.auth import User
from tests.base import BaseTestCase


class TestEventModel(BaseTestCase):
    def test_insert_in_event(self):
        # Add 2 users so user id is a different value to event id
        for username in ('test_username1', 'test_username2'):
            user = User(
                username=username,
                password='test'
            )
            db.session.add(user)
            db.session.commit()

        self.assertEqual(user.id, 2)

        before_insert = datetime.utcnow()
        time.sleep(1)

        event = Event(
            name='test',
            author_id=user.id,
            initial_number_of_tickets=10
        )

        db.session.add(event)
        db.session.commit()

        time.sleep(1)
        after_insert = datetime.utcnow()

        self.assertEqual(event.id, 1)
        self.assertEqual(event.name, 'test')
        self.assertTrue(uuid.UUID(bytes=event.guid))
        self.assertEqual(event.author_id, user.id)
        self.assertEqual(event.initial_number_of_tickets, 10)
        self.assertTrue(before_insert < event.date_created_utc < after_insert)


class TestTicketModel(BaseTestCase):
    def test_insert_in_event(self):
        for username in ('test_username1', 'test_username2'):
            user = User(
                username=username,
                password='test'
            )
            db.session.add(user)
            db.session.commit()

        self.assertEqual(user.id, 2)

        before_insert = datetime.utcnow()
        time.sleep(1)

        event = Event(
            name='test',
            author_id=user.id,
            initial_number_of_tickets=10
        )

        db.session.add(event)
        db.session.commit()

        time.sleep(1)
        after_insert = datetime.utcnow()

        self.assertEqual(event.id, 1)
        self.assertEqual(event.name, 'test')
        self.assertTrue(uuid.UUID(bytes=event.guid))
        self.assertEqual(event.author_id, user.id)
        self.assertEqual(event.initial_number_of_tickets, 10)
        self.assertTrue(before_insert < event.date_created_utc < after_insert)

        before_insert = datetime.utcnow()
        time.sleep(1)

        ticket = Ticket(
            author_id=user.id,
            event_id=event.id
        )

        db.session.add(ticket)
        db.session.commit()

        time.sleep(1)
        after_insert = datetime.utcnow()

        self.assertNotEqual(uuid.UUID(bytes=ticket.guid), uuid.UUID(bytes=event.guid))

        self.assertEqual(ticket.id, 1)
        self.assertTrue(uuid.UUID(bytes=ticket.guid))
        self.assertEqual(ticket.author_id, user.id)
        self.assertEqual(ticket.event_id, event.id)
        self.assertFalse(ticket.is_redeemed)
        self.assertTrue(before_insert < ticket.date_created_utc < after_insert)



if __name__ == '__main__':
    unittest.main()
