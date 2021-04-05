"""
Application initialization.

Flask application initialization, blueprints declaration,
libraries instances creation.
"""

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config.from_object('config')

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
db = SQLAlchemy(app)
mail = Mail(app)
bcrypt = Bcrypt(app)
ma = Marshmallow(app)

from .API.v1_0_0.blueprint import APIv1_0_0  # noqa: E402

app.register_blueprint(APIv1_0_0, url_prefix='/API/v1.0.0')
