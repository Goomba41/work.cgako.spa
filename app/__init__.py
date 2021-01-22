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

# from app.models import OrganizationalStructure

# db.drop_all()
# db.create_all()
# db.session.add(OrganizationalStructure(name="root"))
# db.session.add_all(  # first branch of tree
#     [
#         OrganizationalStructure(name="Отдел1", parent_id=1),
#         OrganizationalStructure(name="Отдел2", parent_id=1),
#         OrganizationalStructure(name="Должность1", parent_id=4),
#     ]
# )
# db.session.commit()

from .API.v1_0_0.blueprint import APIv1_0_0

app.register_blueprint(APIv1_0_0, url_prefix='/API/v1.0.0')
