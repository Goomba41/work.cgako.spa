"""
Database objects.

Flask database models initialization.
"""

from app import ma
from app.models import Roles, Departments, DepartmentsPositions, Users

from marshmallow_sqlalchemy import ModelSchema


class RolesSchema(ModelSchema):
    """System role serialization schema."""

    class Meta:
        """Metadata."""

        model = Roles


class DepartmentsSchema(ModelSchema):
    """Departments serialization schema."""

    class Meta:
        """Metadata."""

        model = Departments


class DepartmentsPositionsSchema(ModelSchema):
    """Departments positions serialization schema."""

    class Meta:
        """Metadata."""

        model = DepartmentsPositions


class UsersSchema(ModelSchema):
    """System user serialization schema."""

    class Meta:
        """Metadata."""

        model = Users
    departments_positions = ma.Nested(DepartmentsPositionsSchema)
    departments = ma.Nested(DepartmentsSchema)
    roles = ma.Nested(RolesSchema)
    links = ma.Hyperlinks(
        {
            "self": ma.URLFor("APIv1_0_0.get_user", values=dict(
                id="<id>", _external=True
            )),
            "collection": ma.URLFor("APIv1_0_0.get_users", values=dict(
                _external=True
            )),
        }
    )
