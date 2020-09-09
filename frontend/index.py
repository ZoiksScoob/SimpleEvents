import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from apps import auth, event, ticket


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
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


if __name__ == '__main__':
    app.run_server(debug=True)
