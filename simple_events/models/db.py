from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

# Instantiate database
db = SQLAlchemy()

# Instantiate bcyrpt
bcrypt = Bcrypt()
