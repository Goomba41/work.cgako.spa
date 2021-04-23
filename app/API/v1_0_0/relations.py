"""Views of API version 1.0.0: Routes for tables relations."""

# from flask import Response, json, request
from flask import request
from flask_babel import _

from .blueprint import APIv1_0_0

from app import db
from app.models import Users, OrganizationalStructure, Modules, user_module, \
    user_structure
# from app.schemas import UsersBaseSchema, OrganizationalStructureSchema, \
#     ModulesBaseSchema

from .utils import json_http_response


@APIv1_0_0.route('/modules/<int:mid>/users/<int:uid>', methods=['POST'])
@APIv1_0_0.route('/users/<int:uid>/modules/<int:mid>', methods=['POST'])
# @token_required
def post_user_module_relation(uid, mid):
    """Post user-module relation."""
    try:

        user = Users.query.get(uid)
        module = Modules.query.get(mid)

        if not user:
            return json_http_response(
                status=404,
                given_message=_(
                    "User with id=%(value)s"
                    " does not exist in database. Please, choose other.",
                    value=uid
                ),
                dbg=request.args.get('dbg', False)
            )
        if not module:
            return json_http_response(
                status=404,
                given_message=_(
                    "Module with id=%(value)s"
                    " does not exist in database. Please, choose other.",
                    value=mid
                ),
                dbg=request.args.get('dbg', False)
            )

        relation = Modules.query.join(user_module).join(Users). \
            filter(
                (user_module.c.user_id == Users.id) &
                (user_module.c.module_id == Modules.id) &
                (user_module.c.module_id == mid) &
                (user_module.c.user_id == uid)
            ).first()
        if relation:
            return json_http_response(
                status=400,
                given_message=_(
                    "User(%(user)s)->Module(%(module)s) relation"
                    " already exist in database. Request ignored.",
                    user=user.login,
                    module=module.name,
                ),
                dbg=request.args.get('dbg', False)
            )

        user.modules.append(module)
        db.session.commit()

        response = json_http_response(
            status=200,
            given_message=_(
                "User(%(user)s)->Module(%(module)s) relation successfully"
                " created!",
                user=user.login,
                module=module.name,
            ),
            dbg=request.args.get('dbg', False)
        )

    except Exception:

        response = json_http_response(dbg=request.args.get('dbg', False))

    return response


@APIv1_0_0.route('/modules/<int:mid>/users/<int:uid>', methods=['DELETE'])
@APIv1_0_0.route('/users/<int:uid>/modules/<int:mid>', methods=['DELETE'])
# @token_required
def delete_user_module_relation(uid, mid):
    """Delete user-module relation."""
    try:

        user = Users.query.get(uid)
        module = Modules.query.get(mid)

        if not user:
            return json_http_response(
                status=404,
                given_message=_(
                    "User with id=%(value)s"
                    " does not exist in database. Please, choose other.",
                    value=uid
                ),
                dbg=request.args.get('dbg', False)
            )
        if not module:
            return json_http_response(
                status=404,
                given_message=_(
                    "Module with id=%(value)s"
                    " does not exist in database. Please, choose other.",
                    value=mid
                ),
                dbg=request.args.get('dbg', False)
            )

        relation = Modules.query.join(user_module).join(Users). \
            filter(
                (user_module.c.user_id == Users.id) &
                (user_module.c.module_id == Modules.id) &
                (user_module.c.module_id == mid) &
                (user_module.c.user_id == uid)
            ).first()

        if not relation:
            return json_http_response(
                status=400,
                given_message=_(
                    "User(%(user)s)->Module(%(module)s) relation"
                    " does not exist in database. Request ignored.",
                    user=user.login,
                    module=module.name,
                ),
                dbg=request.args.get('dbg', False)
            )

        relation.users.remove(user)
        db.session.commit()

        response = json_http_response(
            status=200,
            given_message=_(
                "User(%(user)s)->Module(%(module)s) relation successfully"
                " deleted!",
                user=user.login,
                module=module.name,
            ),
            dbg=request.args.get('dbg', False)
        )

    except Exception:

        response = json_http_response(dbg=request.args.get('dbg', False))

    return response


@APIv1_0_0.route(
    '/organization/structure/elements/<int:sid>/users/<int:uid>',
    methods=['POST']
)
@APIv1_0_0.route(
    '/users/<int:uid>/organization/structure/elements/<int:sid>',
    methods=['POST']
)
# @token_required
def post_user_structure_relation(uid, sid):
    """Post user-structure relation."""
    try:

        user = Users.query.get(uid)
        structure = OrganizationalStructure.query.get(sid)

        if not user:
            return json_http_response(
                status=404,
                given_message=_(
                    "User with id=%(value)s"
                    " does not exist in database. Please, choose other.",
                    value=uid
                ),
                dbg=request.args.get('dbg', False)
            )
        if not structure:
            return json_http_response(
                status=404,
                given_message=_(
                    "Strucure element with id=%(value)s"
                    " does not exist in database. Please, choose other.",
                    value=sid
                ),
                dbg=request.args.get('dbg', False)
            )

        relation = OrganizationalStructure.query.join(user_structure). \
            join(Users). \
            filter(
                (user_structure.c.user_id == Users.id) &
                (user_structure.c.structure_id == OrganizationalStructure.id) &
                (user_structure.c.structure_id == sid) &
                (user_structure.c.user_id == uid)
            ).first()
        if relation:
            return json_http_response(
                status=400,
                given_message=_(
                    "User(%(user)s)->Structure element(%(structure)s) relation"
                    " already exist in database. Request ignored.",
                    user=user.login,
                    structure=structure.name,
                ),
                dbg=request.args.get('dbg', False)
            )
        elif structure.type != 2:
            return json_http_response(
                status=400,
                given_message=_(
                    "User(%(user)s)->Structure element(%(structure)s) relation"
                    " could not be created. User can only be associated with"
                    " structure type 2 (department position).",
                    user=user.login,
                    structure=structure.name,
                ),
                dbg=request.args.get('dbg', False)
            )

        user.structures.append(structure)
        db.session.commit()

        response = json_http_response(
            status=200,
            given_message=_(
                "User(%(user)s)->Module(%(structure)s) relation successfully"
                " created!",
                user=user.login,
                structure=structure.name,
            ),
            dbg=request.args.get('dbg', False)
        )

    except Exception:

        response = json_http_response(dbg=request.args.get('dbg', False))

    return response


@APIv1_0_0.route(
    '/organization/structure/elements/<int:sid>/users/<int:uid>',
    methods=['DELETE']
)
@APIv1_0_0.route(
    '/users/<int:uid>/organization/structure/elements/<int:sid>',
    methods=['DELETE']
)
# @token_required
def delete_user_structure_relation(uid, sid):
    """Delete user-structure relation."""
    try:

        user = Users.query.get(uid)
        structure = OrganizationalStructure.query.get(sid)

        if not user:
            return json_http_response(
                status=404,
                given_message=_(
                    "User with id=%(value)s"
                    " does not exist in database. Please, choose other.",
                    value=uid
                ),
                dbg=request.args.get('dbg', False)
            )
        if not structure:
            return json_http_response(
                status=404,
                given_message=_(
                    "Structure element with id=%(value)s"
                    " does not exist in database. Please, choose other.",
                    value=sid
                ),
                dbg=request.args.get('dbg', False)
            )

        relation = OrganizationalStructure.query.join(user_structure). \
            join(Users). \
            filter(
                (user_structure.c.user_id == Users.id) &
                (user_structure.c.structure_id == OrganizationalStructure.id) &
                (user_structure.c.structure_id == sid) &
                (user_structure.c.user_id == uid)
            ).first()

        if not relation:
            return json_http_response(
                status=400,
                given_message=_(
                    "User(%(user)s)->Structure element(%(structure)s) relation"
                    " does not exist in database. Request ignored.",
                    user=user.login,
                    structure=structure.name,
                ),
                dbg=request.args.get('dbg', False)
            )

        relation.users.remove(user)
        db.session.commit()

        response = json_http_response(
            status=200,
            given_message=_(
                "User(%(user)s)->Module(%(structure)s) relation successfully"
                " deleted!",
                user=user.login,
                structure=structure.name,
            ),
            dbg=request.args.get('dbg', False)
        )

    except Exception:

        response = json_http_response(dbg=request.args.get('dbg', False))

    return response
