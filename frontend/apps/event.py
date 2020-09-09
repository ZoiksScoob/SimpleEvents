import dash
import dash_table
import json
import requests as r
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app, api_url


layout = html.Div([
    html.H1('Event Page'),
    dcc.Tabs(id='event-tabs', value='view-all-tab', children=[
        dcc.Tab(label='View All', value='view-all-tab'),
        dcc.Tab(label='Create', value='create-tab'),
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

        layout = html.Div([
            html.Button('Refresh Events', id='refresh-button'),
            html.Div(id='event-error', children=message, style=style),
            dash_table.DataTable(
                id='events-table',
                columns=[
                    {"name": 'Event Identifier', "id": 'guid'},
                    {"name": 'Event Name', "id": 'name'},
                    {"name": 'Event Date', "id": 'date'},
                    {"name": 'Total Number of Tickets', "id": 'number_of_tickets'},
                    {"name": 'Number of Redeemed Tickets', "id": 'number_of_redeemed_tickets'},
                ],
                data=content)
        ])
        return layout

    elif tab == 'create-tab':
        return 'Create tab'


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

    content, message = get_event_details(session)

    if message is None:
        return content['data'], None

    err_msg = 'Error getting data. ' + message
    return dash.no_update, err_msg
