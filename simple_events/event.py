import uuid
from datetime import datetime
from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
from simple_events.auth import login_required
from simple_events.db import get_db


bp = Blueprint('event', __name__)


@bp.route('/')
@login_required
def index():
    db = get_db()
    events = db.execute(
        'SELECT e.name, e.date,'
        ' SUM(CASE WHEN t.is_redeemed = 0 THEN 1 ELSE 0 END) AS n_unredeemed_tickets'
        ' FROM event e'
        ' JOIN ticket t on t.event_id = e.id'
        ' GROUP BY e.name, e.date'
        ' ORDER BY e.date DESC'
    ).fetchall()
    return render_template('event/index.html', events=events)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        date = request.form['date']
        n_tickets = request.form['n_tickets']
        error = None

        # Data validation on the data sent in the request
        if not name:
            error = 'Name of the event is required.'

        if not date:
            error = 'Date of the event is required.'
        else:
            try:
                date = datetime.strptime(date, '%Y-%m-%d').date()
            except ValueError:
                error = 'A valid date of the format yyyy-mm-dd is required.'

        if not n_tickets:
            error = 'An initial number of tickets of the event is required.'
        elif not n_tickets.isdigit() and int(n_tickets) > 0:
            error = 'The initial number of tickets must be an integer greater than 0.'
        else:
            n_tickets = int(n_tickets)

        if error is not None:
            flash(error)
        else:
            db = get_db()

            cursor = db.cursor()

            # Create the event
            event_uuid = uuid.uuid4()

            cursor.execute(
                'INSERT INTO event '
                ' (name, date, initial_number_of_tickets, guid, author_id)'
                ' VALUES (?, ?, ?, ?, ?)',
                (name, date, n_tickets, str(event_uuid), g.user['id'])
            )

            new_event_id = cursor.lastrowid

            # Create the tickets
            ticket_data = ((g.user['id'], new_event_id, str(uuid.uuid4()))
                           for _ in range(n_tickets))

            cursor.executemany(
                'INSERT INTO ticket (author_id, event_id, guid) VALUES (?, ?, ?)',
                ticket_data
            )

            db.commit()

            return redirect(url_for('event.index'))

    return render_template('event/create.html')
