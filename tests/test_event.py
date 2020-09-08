import json
import unittest
import uuid
from datetime import datetime

from tests.base import BaseTestCase
from simple_events.models import db
from simple_events.models.event import Event, Ticket
from simple_events.models.auth import User


class TestEventBlueprint(BaseTestCase):
    def create_event(self, name, initial_number_of_tickets, auth_token):
        return self.client.post(
                'event/create',
                data=json.dumps(dict(
                    name=name,
                    initial_number_of_tickets=initial_number_of_tickets
                )),
                content_type='application/json',
                headers=dict(Authorization=auth_token)
            )


class TestEvent(TestEventBlueprint):
    def test_creating_event(self):
        with self.client:
            start_time = datetime.utcnow()

            reg_response = self.register_user('dummy_username', '12345678')
            reg_data = json.loads(reg_response.data.decode())
            self.assertTrue(reg_data['status'] == 'success')
            self.assertTrue(reg_data['message'] == 'Successfully registered.')
            self.assertTrue(reg_data['auth_token'])
            self.assertTrue(reg_response.content_type == 'application/json')
            self.assertEqual(reg_response.status_code, 200)

            auth_token = json.loads(reg_response.data.decode("utf-8"))['auth_token']

            event_response = self.create_event(
                name='test',
                initial_number_of_tickets=5,
                auth_token=auth_token)

            event_data = json.loads(event_response.data.decode())

            self.assertEqual(event_response.status_code, 200)
            self.assertEqual(event_data['status'], 'success')
            self.assertEqual(event_data['message'], 'Successfully created event "test".')
            self.assertTrue(event_data['eventIdentifier'])
            self.assertEqual(event_response.content_type, 'application/json')

            eventIdentifier = event_data['eventIdentifier']
            eventIdentifier = uuid.UUID(eventIdentifier)

            event = Event.query.filter_by(guid=eventIdentifier.bytes).first()

            author_id = User.decode_auth_token(auth_token)

            self.assertEqual(event.name, 'test')
            self.assertEqual(event.author_id, author_id)
            self.assertEqual(event.initial_number_of_tickets, 5)
            self.assertTrue(uuid.UUID(bytes=event.guid))
            self.assertTrue(start_time < event.date_created_utc < datetime.utcnow())

            tickets = Ticket.query.filter(db.and_(
                Ticket.author_id == event.author_id,
                Ticket.event_id == event.id
            )).all()

            self.assertEqual(len(tickets), 5)

    def test_creating_event_with_invalid_token(self):
        with self.client:
            event_response = self.create_event(
                name='test',
                initial_number_of_tickets=5,
                auth_token='invalid_token')

            event_data = json.loads(event_response.data.decode())

            self.assertEqual(event_response.status_code, 401)
            self.assertEqual(event_data['status'], 'fail')
            self.assertEqual(event_response.content_type, 'application/json')

            event = Event.query.first()

            self.assertFalse(event)

            tickets = Ticket.query.all()

            self.assertFalse(tickets)

    def test_creating_event_without_tickets(self):
        with self.client:
            event_response = self.create_event(
                name='test',
                initial_number_of_tickets=-1,
                auth_token='invalid_token')

            event_data = json.loads(event_response.data.decode())

            self.assertEqual(event_response.status_code, 400)
            self.assertTrue(event_data['errors'])
            
            self.assertEqual(event_data['message'], 'Input payload validation failed')
            self.assertEqual(event_data['errors']['initial_number_of_tickets'], 'initial_number_of_tickets must be an integer >= 1.')
            self.assertEqual(event_response.content_type, 'application/json')

            event = Event.query.first()

            self.assertFalse(event)

            tickets = Ticket.query.all()

            self.assertFalse(tickets)


if __name__ == '__main__':
    unittest.main()
