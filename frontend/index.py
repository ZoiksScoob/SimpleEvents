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
    html.Div(id='page-content')
])


@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname in ('/auth', '', '/') :
        return auth.layout
    elif pathname == '/event':
        return event.layout
    elif pathname == '/ticket':
        return ticket.layout
    else:
        return '404: Page Not Found'


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
