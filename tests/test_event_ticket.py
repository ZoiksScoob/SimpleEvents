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
        """ Test creating an event """
        with self.client:
            start_time = datetime.utcnow()

            reg_response = self.register_user('dummy_username', '12345678')

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
        """ Test creating an event with an invalid token """
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
        """ Test creating an event with an invalid number of tickets """
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

    def test_checking_status_of_event(self):
        """ Test getting status of an event """
        with self.client:
            reg_response = self.register_user('dummy_username', '12345678')

            auth_token = json.loads(reg_response.data.decode("utf-8"))['auth_token']

            event_response = self.create_event(
                name='test',
                initial_number_of_tickets=2,
                auth_token=auth_token)

            event_data = json.loads(event_response.data.decode())

            status_response = self.client.get(
                f'event/status/{event_data["eventIdentifier"]}',
                content_type='application/json',
                headers=dict(Authorization=auth_token)
            )

            status_data = json.loads(status_response.data.decode())

            self.assertEqual(status_response.status_code, 200)
            self.assertEqual(status_data['status'], 'success')
            self.assertTrue(status_data['data'])
            self.assertEqual(status_data['data']['name'], 'test')
            self.assertEqual(status_data['data']['number_of_tickets'], 2)
            self.assertEqual(status_data['data']['number_of_redeemed_tickets'], 0)
            self.assertEqual(status_response.content_type, 'application/json')

    def test_downloading_unredeemed_tickets_of_event(self):
        """ Test download of unredeemed tickets of an event """
        with self.client:
            reg_response = self.register_user('dummy_username', '12345678')

            auth_token = json.loads(reg_response.data.decode("utf-8"))['auth_token']

            event_response = self.create_event(
                name='test',
                initial_number_of_tickets=2,
                auth_token=auth_token)

            event_data = json.loads(event_response.data.decode())

            download_response = self.client.get(
                f'event/download/{event_data["eventIdentifier"]}',
                content_type='application/json',
                headers=dict(Authorization=auth_token)
            )

            download_data = json.loads(download_response.data.decode())

            self.assertEqual(download_response.status_code, 200)
            self.assertEqual(download_data['status'], 'success')
            self.assertTrue(download_data['data'])
            self.assertTrue(isinstance(download_data['data']['ticketIdentifiers'], list))
            self.assertEqual(len(download_data['data']['ticketIdentifiers']), 2)
            self.assertEqual(download_response.content_type, 'application/json')

            eventIdentifier = uuid.UUID(event_data["eventIdentifier"])
            ticketIdentifiers = [uuid.UUID(id_).bytes for id_ in download_data['data']['ticketIdentifiers']]

            tickets = db.session.query(
                    db.func.count(Ticket.id).label('n')
                )\
                .join(Event)\
                .filter(db.and_(
                    Event.guid == eventIdentifier.bytes,
                    Ticket.is_redeemed == False,
                    Ticket.guid.in_(ticketIdentifiers)
                ))\
                .first()

            self.assertEqual(tickets.n, 2)

    def test_adding_tickets_to_event(self):
        """ Test adding tickets to an event """
        reg_response = self.register_user('dummy_username', '12345678')

        auth_token = json.loads(reg_response.data.decode("utf-8"))['auth_token']

        event_response = self.create_event(
            name='test',
            initial_number_of_tickets=2,
            auth_token=auth_token)

        event_data = json.loads(event_response.data.decode())

        add_response = self.client.put(
            f'event/add/{event_data["eventIdentifier"]}',
            content_type='application/json',
            headers=dict(Authorization=auth_token),
            data=json.dumps(dict(additionalNumberOfTickets=3)),
        )

        add_data = json.loads(add_response.data.decode())

        self.assertEqual(add_response.status_code, 200)
        self.assertEqual(add_response.content_type, 'application/json')
        self.assertEqual(add_data['status'], 'success')

        status_response = self.client.get(
            f'event/status/{event_data["eventIdentifier"]}',
            content_type='application/json',
            headers=dict(Authorization=auth_token)
        )

        status_data = json.loads(status_response.data.decode())

        self.assertEqual(status_data['data']['number_of_tickets'], 5)


class TestTicket(TestEventBlueprint):
    def test_redeem_a_ticket(self):
        """ Test redeeming a ticket """
        # Make user
        reg_response = self.register_user('dummy_username', '12345678')

        auth_token = json.loads(reg_response.data.decode("utf-8"))['auth_token']

        # Make event
        event_response = self.create_event(
            name='test',
            initial_number_of_tickets=2,
            auth_token=auth_token)

        event_data = json.loads(event_response.data.decode())

        # Get ticket ids
        download_response = self.client.get(
                f'event/download/{event_data["eventIdentifier"]}',
                content_type='application/json',
                headers=dict(Authorization=auth_token)
            )

        download_data = json.loads(download_response.data.decode())

        ticketIdentifier = download_data['data']['ticketIdentifiers'][0]

        # Redeem
        redeem_response = self.client.get(
                f'/redeem/{ticketIdentifier}',
                content_type='application/json',
            )

        self.assertTrue(redeem_response.status_code, 200)

        # See the unredeemed tickets
        download_response = self.client.get(
                f'event/download/{event_data["eventIdentifier"]}',
                content_type='application/json',
                headers=dict(Authorization=auth_token)
            )

        download_data = json.loads(download_response.data.decode())

        ticketIdentifiers = download_data['data']['ticketIdentifiers']

        self.assertEqual(len(ticketIdentifiers), 1)
        self.assertTrue(ticketIdentifier not in ticketIdentifiers)

        # Check you can't redeem again
        redeem_response = self.client.get(
                f'/redeem/{ticketIdentifier}',
                content_type='application/json',
            )

        self.assertTrue(redeem_response.status_code, 410)

        # Check no other ticket has been accidentally redeemed
        download_response = self.client.get(
                f'event/download/{event_data["eventIdentifier"]}',
                content_type='application/json',
                headers=dict(Authorization=auth_token)
            )

        download_data = json.loads(download_response.data.decode())

        ticketIdentifiers = download_data['data']['ticketIdentifiers']

        self.assertEqual(len(ticketIdentifiers), 1)
        self.assertTrue(ticketIdentifier not in ticketIdentifiers)



if __name__ == '__main__':
    unittest.main()
