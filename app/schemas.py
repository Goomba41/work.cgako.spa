"""
Database objects.

Flask database models initialization.
"""

from app import ma
from app.models import OrganizationalStructure, Users, ModulesTypes, \
 Modules, Emails

from marshmallow_sqlalchemy import ModelSchema


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


class ModulesBaseSchema(ModelSchema):
    """Models base serialization schema."""

    class Meta:
        """Metadata."""

        model = Modules


class ModulesTypesSchema(ModelSchema):
    """Models types serialization schema."""

    class Meta:
        """Metadata."""

        model = ModulesTypes

    modules = ma.Nested(ModulesBaseSchema, many=True)

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


class ModulesSchema(ModulesBaseSchema):
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
    type = ma.Nested(ModulesTypesSchema(exclude=("modules",)))
    users = ma.Nested(UsersBaseSchema(exclude=("modules",), many=True))


class EmailsSchema(ModulesBaseSchema):
    """Emails serialization schema."""

    class Meta:
        """Metadata."""

        model = Emails

    links = ma.Hyperlinks(
        {
            "self": ma.URLFor(
                "APIv1_0_0.get_emails_item",
                values=dict(
                    id="<id>", _external=True
                )
            ),
            "collection": ma.URLFor(
                "APIv1_0_0.get_emails",
                values=dict(
                    _external=True
                )
            ),
        }
    )
    # type = ma.Nested(UsersBaseSchema(exclude=("emails",)))
