import os
import dash


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.config.suppress_callback_exceptions = True

server = app.server

api_url = os.environ.get('API_URL', 'http://localhost:5000/')
