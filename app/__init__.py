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
    language = None
    languages = app.config['LANGUAGES']

    # 5. Take language from AcceptLanguages Header or request
    language = request.accept_languages.best_match(languages)

    # 4. Take language from Cookie
    cookie_parameter = request.cookies.get('lang', None)
    if cookie_parameter and cookie_parameter in languages:
        language = cookie_parameter

    # 3. Take language from DB (from user settings)
    # Make later after user edit

    # 2. Take language from domain
    host = request.host
    domain_parse_list = host.split('.')
    if domain_parse_list[0] in languages:
        language = domain_parse_list[0]

    # 1. Take language from request argument &lang=
    request_parameter = request.args.get('lang', None)
    if request_parameter and request_parameter in languages:
        language = request_parameter

    return language
