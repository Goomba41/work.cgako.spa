"""
Database objects.

Flask database models initialization.
"""

from app import ma
from app.models import Roles, OrganizationalStructure, Users, ModulesTypes, \
 Modules

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


# class UsersStructureSchema(UsersBaseSchema):
#     """System user serialization schema."""
#
#     class Meta:
#         """Metadata."""
#
#         exclude = ("position", "last_login", "about_me", "password",
#                    "roles.users", "socials")

    # roles = ma.Nested(RolesSchema)


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
    # users = ma.Nested(UsersStructureSchema, many=True)

    links = ma.Hyperlinks(
        {
            "self": ma.URLFor(
                "APIv1_0_0.get_organizational_structure_element",
                values=dict(
                    id="<id>", _external=True
                )
            ),
            "collection": ma.URLFor(
                "APIv1_0_0.get_organizational_structure",
                values=dict(
                    _external=True
                )
            ),
        }
    )


# class UsersSchema(UsersBaseSchema):
#     """System user serialization schema."""
    #
    # position = ma.Nested(
    #     OrganizationalStructureSchema
    # )
    # roles = ma.Nested(RolesSchema)


class ModulesSchema(ModelSchema):
    """Models serialization schema."""

    class Meta:
        """Metadata."""

        model = Modules

    links = ma.Hyperlinks(
        {
            "self": ma.URLFor(
                "APIv1_0_0.get_modules_item",
                values=dict(
                    id="<id>", _external=True
                )
            ),
            "collection": ma.URLFor(
                "APIv1_0_0.get_modules",
                values=dict(
                    _external=True
                )
            ),
        }
    )


class ModulesTypesSchema(ModelSchema):
    """Models types serialization schema."""

    class Meta:
        """Metadata."""

        model = ModulesTypes

    modules = ma.Nested(ModulesSchema, many=True)

    links = ma.Hyperlinks(
        {
            "self": ma.URLFor(
                "APIv1_0_0.get_modules_types_item",
                values=dict(
                    id="<id>", _external=True
                )
            ),
            "collection": ma.URLFor(
                "APIv1_0_0.get_modules_types",
                values=dict(
                    _external=True
                )
            ),
        }
    )
