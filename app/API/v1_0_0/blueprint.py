"""API blueprint with separated views import."""

from flask import Blueprint

APIv1_0_0 = Blueprint('APIv1_0_0', __name__)

from . import profile
from . import users
from . import organizational_structure
