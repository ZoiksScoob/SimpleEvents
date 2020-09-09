import dash
import dash_table
import json
import requests as r
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from datetime import datetime

from app import app, api_url


layout = html.Div([
    html.H1('Event Page'),
    dcc.Tabs(id='event-tabs', value='view-all-tab', children=[
        dcc.Tab(label='View All', value='view-all-tab'),
        dcc.Tab(label='Create', value='create-tab'),
        dcc.Tab(label='Ticket', value='ticket-tab'),
    ]),
    html.Div(id='event-tabs-content'),
])


def get_event_details(session):
    headers = {
        'Authorization': session['token'], 
        'content-type': 'application/json'
        }

    response = r.get(api_url + 'event/all', headers=headers)

    content = json.loads(response.content.decode())
 
    if response.status_code == 200:
        return content['data'], None
    return None, content['message']


# Render tab content
@app.callback(
    Output('event-tabs-content', 'children'),
    [Input('event-tabs', 'value')],
    state=[State('session', 'data')]
)
def render_content(tab, session):
    if tab == 'view-all-tab':
        content, message = get_event_details(session)

        style = {'color': 'red', 'fontSize': 14} if message is None else {'fontSize': 14}

        n_tickets_add_input = dbc.FormGroup([
            dbc.Label("Additional No. Tickets", html_for="event-add-n_tickets", width=5),
            dbc.Col(
                dbc.Input(
                    type="number",
                    id="event-add-n_tickets-row",
                    placeholder="Enter additional number of tickets for selected event",
                    min=1
                ),
                width=20)
            ], row=True)

        add_button = dbc.FormGroup([dbc.Button('Add', id='add-button')])

        add_message = dbc.FormGroup(html.Div(id='add-message'))

        layout = html.Div([
            dbc.Form([n_tickets_add_input, add_button, add_message]),
            html.Button('Refresh Events', id='refresh-button'),
            html.Button('Download Unredeemed Tickets of Selected Event', id='download-button'),
            html.Div(id='event-error', children=message, style={'color': 'red', 'fontSize': 14}),
            html.Div(id='download-error', style=style),
            dash_table.DataTable(
                id='events-table',
                columns=[
                    {"name": 'Event Identifier', "id": 'guid'},
                    {"name": 'Event Name', "id": 'name'},
                    {"name": 'Event Date', "id": 'date'},
                    {"name": 'Total Number of Tickets', "id": 'number_of_tickets'},
                    {"name": 'Number of Redeemed Tickets', "id": 'number_of_redeemed_tickets'},
                ],
                data=content,
                row_selectable="single",
                filter_action="native",
                sort_action="native",
                page_action="native",
                page_current= 0,
                page_size= 25)
        ])
        return layout

    elif tab == 'create-tab':
        name_input = dbc.FormGroup([
            dbc.Label("Name", html_for="event-name", width=2),
            dbc.Col(
                dbc.Input(
                    type="text",
                    id="event-name-row",
                    placeholder="Enter name of event",
                    minLength=1,
                    maxLength=255,
                ),
                width=10)
            ], row=True)

        date_input = dbc.FormGroup([
            dbc.Label("Date", html_for="event-date", width=2),
            dbc.Col(
                dcc.DatePickerSingle(
                    min_date_allowed=datetime.now().date(),
                    id="event-date-row",
                    initial_visible_month=datetime.now().date(),
                    display_format='DD/MM/YYYY'
                ),
                width=10)
            ], row=True)

        n_tickets_input = dbc.FormGroup([
            dbc.Label("Initial No. Tickets", html_for="event-n_tickets", width=2),
            dbc.Col(
                dbc.Input(
                    type="number",
                    id="event-n_tickets-row",
                    placeholder="Enter initial numver of tickets of event",
                    min=1
                ),
                width=10)
            ], row=True)

        button = dbc.FormGroup([dbc.Button('Create', id='create-button')])

        message = dbc.FormGroup(html.Div(id='create-message'))

        layout = dbc.Form([name_input, date_input, n_tickets_input, button, message])

        return layout

    elif tab == 'ticket-tab':
        ticket_input = dbc.FormGroup([
            dbc.Label("Ticket Identifier", html_for="event-ticket", width=2),
            dbc.Col(
                dbc.Input(
                    type="text",
                    id="event-ticket-row",
                    placeholder="Enter identifier of a ticket",
                    minLength=1,
                    maxLength=50,
                ),
                width=10)
            ], row=True)

        status_button = dbc.FormGroup([dbc.Button('Check Status', id='status-button')])

        status_message = dbc.Alert(id='status-message')

        layout = dbc.Form([ticket_input, status_button, status_message])

        return layout


@app.callback(
    [
        Output('events-table', 'data'),
        Output('event-error', 'children'),
    ],
    [Input('refresh-button', 'n_clicks')],
    state=[State('session', 'data')]
)
def populate_table(n_clicks, session):
    if not n_clicks:
        raise PreventUpdate

    data, message = get_event_details(session)

    if message is None:
        return data, None

    err_msg = 'Error getting data. ' + message
    return dash.no_update, err_msg


@app.callback(
    [
        Output('create-message', 'children'),
        Output('create-message', 'style'),
    ],
    [Input('create-button', 'n_clicks')],
    state=[
        State('session', 'data'),
        State('event-name-row', 'value'),
        State('event-date-row', 'date'),
        State('event-n_tickets-row', 'value')
    ]
)
def create_event(n_clicks, session, name, date, n_tickets):
    if not n_clicks:
        raise PreventUpdate

    if not all((name, date, n_tickets)):
        return 'Please input a value for all inputs.', {'color': 'red', 'fontSize': 14}

    headers = {
        'Authorization': session['token'],
        'content-type': 'application/json'
        }

    payload = {
        'name': name,
        'date': date,
        'initial_number_of_tickets': n_tickets
    }

    response = r.post(
        api_url + 'event/create',
        headers=headers,
        data=json.dumps(payload)
        )

    content = json.loads(response.content.decode())

    if response.status_code == 200:
        return content['message'], {'color': 'green', 'fontSize': 14}

    return content['message'], {'color': 'red', 'fontSize': 14}


@app.callback(
    [
        Output('add-message', 'children'),
        Output('add-message', 'style'),
    ],
    [Input('add-button', 'n_clicks')],
    state=[
        State('session', 'data'),
        State('event-add-n_tickets-row', 'value'),
        State('events-table', 'selected_rows'),
        State('events-table', 'data')
    ]
)
def add_to_event(n_clicks, session, n_tickets, event, rows):
    if not n_clicks:
        raise PreventUpdate

    if not event:
        return 'Please select an event', {'color': 'red', 'fontSize': 14}
    elif not n_tickets:
        return 'Please input the number of additional tickets you would like to add', {'color': 'red', 'fontSize': 14}

    headers = {
        'Authorization': session['token'],
        'content-type': 'application/json'
        }

    payload = {
        'additionalNumberOfTickets': n_tickets,
    }

    response = r.put(
        api_url + f"event/add/{rows[event[0]]['guid']}",
        headers=headers,
        data=json.dumps(payload)
        )

    content = json.loads(response.content.decode())

    if response.status_code == 200:
        return content['message'], {'color': 'green', 'fontSize': 14}

    return content['message'], {'color': 'red', 'fontSize': 14}


@app.callback(
    [
        Output('status-message', 'children'),
        Output('status-message', 'color'),
    ],
    [Input('status-button', 'n_clicks')],
    state=[
        State('session', 'data'),
        State('event-ticket-row', 'value')
    ]
)
def check_ticket_status(n_clicks, session, ticket_identifier):
    if not n_clicks:
        raise PreventUpdate
    elif not ticket_identifier:
        raise PreventUpdate

    headers = {
        'Authorization': session['token'], 
        'content-type': 'application/json'
        }

    response = r.get(
        api_url + f'status/{ticket_identifier}', 
 
        headers=headers)

    content = json.loads(response.content.decode())

    color = 'success' if (response.status_code == 200) else 'danger'

    return content['message'], color


@app.callback(
    [
        Output('download-error', 'children')
    ],
    [Input('download-button', 'n_clicks')],
    state=[
        State('session', 'data'),
        State('events-table', 'selected_rows'),
        State('events-table', 'data')
    ]
)
def download_event_unredeemed_tickets(n_clicks, session, event, rows):
    if not n_clicks:
        raise PreventUpdate
    elif not event:
        return 'Please select an event.'
    headers = {
        'Authorization': session['token'], 
        'content-type': 'application/json'
        }

    response = r.get(
        api_url + f"event/download/{rows[event[0]]['guid']}", 
        headers=headers)

    content = json.loads(response.content.decode())

    if response.status_code == 200:
        return None
    return content['message']
