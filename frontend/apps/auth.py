from dash import no_update
from dash.exceptions import PreventUpdate
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dep

from app import app, api_url


layout = html.Div([
    html.Div('Authentication Page')
    dcc.Tabs(id='authentication-tabs', value='register-tab', children=[
        dcc.Tab(label='Login', value='login-tab'),
        dcc.Tab(label='Register', value='register-tab'),
    ]),
    html.Div(id='authentication-tabs-content')
    html.Div(id='error', style={'color': 'red', 'fontSize': 14}))
])


# Forms
def make_form(button_name):
    return html.Div([,
        dcc.Input(
                id=f"input-username",
                type="text",
                placeholder="username",
                minLength=1,
                maxLength=255
            ),
        dcc.Input(
                id=f"input-password",
                type="password",
                placeholder="password",
                minLength=8,
                maxLength=255
            ),
        html.Button(button_name, id=f'button')
        ])


# Render tab content
@app.callback(
    dep.Output('authentication-tabs-content', 'children'),
    [dep.Input('authentication-tabs', 'value')]
)
def render_content(tab):
    if tab == 'register-tab':
        return make_form('Register')
    elif tab == 'login-tab':
        return make_form('Login')


# Make form content
@app.callback(
    [
        dep.Output('session', 'data'),
        dep.Output('error', 'children')
    ],
    [dep.Input('button', 'n_clicks')],
    [
        dep.State('authentication-tabs', 'value')
        dep.State('session', 'data'),
        dep.State('input-username', 'value'),
        dep.State('input-password', 'value'),

    ]
)
def on_click(n_clicks, tab, session, username, password):
    if n_clicks is None:
        # prevent the None callbacks is important with the store component.
        # you don't want to update the store for nothing.
        raise PreventUpdate

    if tab == 'register-tab':
        endpoint = 'auth/register'
    elif tab == 'login-tab':
        endpoint = 'auth/login'

    headers = {'content-type': 'application/json'}

    payload = {
        'username': username,
        'password': password
    }

    response = r.post(
        api_url + endpoint,
        data=json.dumps(payload),
        headers=headers,
    )

    content = json.loads(response.content.decode())

    if response.status_code == 200:
        session = session or {'token': None}

        session['token'] = content['auth_token']

        return session, ''

    return no_update, content['message']
