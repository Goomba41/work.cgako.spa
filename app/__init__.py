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
#
# node = OrganizationalStructure.query.filter(OrganizationalStructure.id == 12).first()
# db.session.delete(node)
# OrganizationalStructure.rebuild_tree(db.session, '1')

# db.drop_all()
# db.create_all()
# db.session.add(OrganizationalStructure(name="КОГБУ «ЦГАКО»"))
# db.session.add_all(  # first branch of tree
#     [
#         OrganizationalStructure(name="Администрация", parent_id=1, type=1),
#         OrganizationalStructure(name="Информационно-поисковых систем", parent_id=1, type=1),
#         OrganizationalStructure(name="Программист", parent_id=3, type=2),
#         OrganizationalStructure(name="Подотдел", parent_id=2, type=1),
#         OrganizationalStructure(name="Должность", parent_id=5, type=2),
#         OrganizationalStructure(name="Должность", parent_id=2, type=2),
#     ]
# )
# db.session.commit()

from .API.v1_0_0.blueprint import APIv1_0_0  # noqa: E402

app.register_blueprint(APIv1_0_0, url_prefix='/API/v1.0.0')
