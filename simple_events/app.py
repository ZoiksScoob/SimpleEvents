from . import create_app
from flask import Blueprint
from flask_restful import Api


app = create_app(__name__)
api_bp = Blueprint('api', __name__)
api = Api(api_bp)


if __name__ == '__main__':
    app.run(debug=True)
