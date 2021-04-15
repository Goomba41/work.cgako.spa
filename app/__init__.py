"""
Application initialization.

Flask application initialization, blueprints declaration,
libraries instances creation.
"""

from flask import Flask, request
from flask_bcrypt import Bcrypt
from flask_babel import Babel
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
babel = Babel(app)
ma = Marshmallow(app)

from .API.v1_0_0.blueprint import APIv1_0_0  # noqa: E402

app.register_blueprint(APIv1_0_0, url_prefix='/API/v1.0.0')


@babel.localeselector
def get_locale():
    """Get preferred language from HTTP header."""
    print(request.accept_languages)
    return request.accept_languages.best_match(app.config['LANGUAGES'])
    # return "ru"
