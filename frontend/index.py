import json
import dash
import requests as r
import dash_core_components as dcc
import dash_html_components as html

from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State

from app import app, api_url
from apps import auth, event, ticket


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='hidden-div-for-auth-page-redirect-callback', style={'display': 'none'}),
    dcc.Store(id='session', storage_type='session'),
    html.Div([
        html.Div([
            'Your session has expired, please click to continue to login page.',
            html.Button('Go to Login', id='session-expired-dialog-button')
            ], 
            id='session-expired-dialog',
            style={'display': 'none'}),
        html.Div(id='page-content')
    ])
])


def is_token_valid(session):
    # Put session token validation after going to auth page
    if session and session['token']:
        headers = {'Authorization': session['token'], 'content-type': 'application/json'}
        response = r.get(api_url + 'auth/status', headers=headers)
        return response.status_code == 200
    return False


@app.callback(
    [
        Output('page-content', 'children'),
        Output('session-expired-dialog', 'style'),
    ],
    [Input('url', 'pathname')],
    state=[State('session', 'data')]
)
def display_page(pathname, session):
    hide_session_expiry_div = {'display': 'none'}

    if pathname in ('/auth', '', '/'):
        return auth.layout, hide_session_expiry_div

    token_is_valid = is_token_valid(session)

    if not token_is_valid:
        return '', None
    elif pathname == '/event':
        return event.layout, hide_session_expiry_div
    elif pathname == '/ticket':
        return ticket.layout, hide_session_expiry_div
    else:
        return '404: Page Not Found', hide_session_expiry_div


@app.callback(
    Output('url', 'pathname'),
    [
        Input('session-expired-dialog-button', 'n_clicks'),
        Input('hidden-div-for-auth-page-redirect-callback', 'children'),
    ]
)
def redirect(*args):
    print('redirect')
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate

    if ctx.triggered[0]['prop_id'] == 'session-expired-dialog-button.n_clicks':
        return '/auth'
    return ctx.triggered[0]["value"]


if __name__ == '__main__':
    app.run_server(debug=True)
