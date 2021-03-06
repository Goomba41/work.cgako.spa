"""API blueprint with separated views import."""

from flask import Blueprint

APIv1_0_0 = Blueprint('APIv1_0_0', __name__)

from . import relations  # noqa: F401, E402
from . import users  # noqa: F401, E402
from . import organizational_structure  # noqa: F401, E402
from . import modules  # noqa: F401, E402
from . import emails  # noqa: F401, E402
from . import passwords  # noqa: F401, E402
