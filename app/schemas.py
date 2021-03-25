"""
Database objects.

Flask database models initialization.
"""

from app import ma
from app.models import Roles, OrganizationalStructure, Users

from marshmallow_sqlalchemy import ModelSchema


class RolesSchema(ModelSchema):
    """System role serialization schema."""

    class Meta:
        """Metadata."""

        model = Roles


class UsersBaseSchema(ModelSchema):
    """System user serialization schema."""

    class Meta:
        """Metadata."""

        model = Users

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


class UsersStructureSchema(UsersBaseSchema):
    """System user serialization schema."""

    class Meta:
        """Metadata."""

        exclude = ("position", "last_login", "about_me", "password",
                   "roles.users", "socials")

    roles = ma.Nested(RolesSchema)


class OrganizationalStructureSchema(ModelSchema):
    """Departments positions serialization schema."""

    class Meta:
        """Metadata."""

        model = OrganizationalStructure
        exclude = ("children",)

    parent = ma.Nested(
        lambda: OrganizationalStructureSchema(exclude=("parent",))
    )
    children = ma.Nested(
        lambda: OrganizationalStructureSchema(exclude=("parent", "children",)),
        many=True
    )
    users = ma.Nested(UsersStructureSchema, many=True)


class UsersSchema(UsersBaseSchema):
    """System user serialization schema."""

    position = ma.Nested(
        OrganizationalStructureSchema
    )
    roles = ma.Nested(RolesSchema)
