"""Views of API version 1.0.0: Routes for tables relations."""

from flask import Response, json, request, url_for
from flask_babel import _

from .blueprint import APIv1_0_0

from app import db
from app.models import Users, OrganizationalStructure, Modules, user_module, \
    user_structure, Emails, Passwords
from app.schemas import EmailsSchema, PasswordsSchema
# , OrganizationalStructureSchema, \
#     ModulesBaseSchema

from .utils import json_http_response, pagination_of_list, \
    marshmallow_excluding_converter, marshmallow_only_fields_converter, \
    sqlalchemy_filters_converter, sqlalchemy_orders_converter


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


@APIv1_0_0.route('/users/<int:uid>/emails', methods=['GET'])
# @token_required
def get_user_emails_relation(uid):
    """Get user-emails relation."""
    try:
        # Get parameters from request
        filters_list = request.args.get('filters')
        exclusions_list = request.args.get('exclude')
        columns_list = request.args.get('columns')
        orders_list = request.args.get('order_by')
        # ----------------------------------------------------------------------

        # Forming dumping parameters
        dump_params = {'many': True}

        # Check if values of getted parameters exist in database table
        # and set dump settings
        try:
            if exclusions_list:
                exclusions_list = marshmallow_excluding_converter(
                    Emails, exclusions_list
                )
                if 'id' in exclusions_list:
                    exclusions_list.remove('id')
                dump_params['exclude'] = exclusions_list
            if columns_list:
                columns_list = marshmallow_only_fields_converter(
                    Emails, columns_list
                )
                dump_params['only'] = ["id"] + columns_list
        except Exception as error:
            return error.args[0]
        #
        schema = EmailsSchema(**dump_params)
        # ----------------------------------------------------------------------

        user = Users.query.get(uid)

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

        # Make empty base query and if
        # filters and orders exist - add it to query
        emails = user.emails

        if filters_list:
            filters_list = ', '.join(
                [
                    x.strip() for x in filters_list.split(",")
                    if "user_id" not in x
                ]
            )
            filters_list += f", user_id:==:{uid}"
            try:
                filters_list = sqlalchemy_filters_converter(
                    Emails,
                    filters_list
                )
            except Exception as error:
                return error.args[0]
            emails = emails.filter(*filters_list)
        if orders_list:
            try:
                orders_list = sqlalchemy_orders_converter(
                    Emails, orders_list
                )
            except Exception as error:
                return error.args[0]
            emails = emails.order_by(*orders_list)
        # ----------------------------------------------------------------------

        emails_dump = schema.dump(emails)

        # Paginating results of dumping
        # Probably would best is pagination in sqlalchemy query?
        emails_dump = pagination_of_list(
            emails_dump,
            url_for(
                '.get_modules',
                _external=True
            ),
            query_params=request.args
        )
        # ----------------------------------------------------------------------

        response = Response(
            response=json.dumps(emails_dump),
            status=200,
            mimetype='application/json'
        )

    except Exception:

        response = json_http_response(dbg=request.args.get('dbg', False))

    return response


@APIv1_0_0.route('/users/<int:uid>/passwords', methods=['GET'])
# @token_required
def get_user_passwords_relation(uid):
    """Get user-passwords relation."""
    try:
        # Get parameters from request
        filters_list = request.args.get('filters')
        exclusions_list = request.args.get('exclude')
        columns_list = request.args.get('columns')
        orders_list = request.args.get('order_by')
        # ----------------------------------------------------------------------

        # Forming dumping parameters
        dump_params = {'many': True}

        # Check if values of getted parameters exist in database table
        # and set dump settings
        try:
            if exclusions_list:
                exclusions_list = marshmallow_excluding_converter(
                    Passwords, exclusions_list
                )
                if 'id' in exclusions_list:
                    exclusions_list.remove('id')
                dump_params['exclude'] = exclusions_list
            if columns_list:
                columns_list = marshmallow_only_fields_converter(
                    Passwords, columns_list
                )
                dump_params['only'] = ["id"] + columns_list
        except Exception as error:
            return error.args[0]
        #
        schema = PasswordsSchema(**dump_params)
        # ----------------------------------------------------------------------

        user = Users.query.get(uid)

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

        # Make empty base query and if
        # filters and orders exist - add it to query
        passwords = user.passwords

        if filters_list:
            filters_list = ', '.join(
                [
                    x.strip() for x in filters_list.split(",")
                    if "user_id" not in x
                ]
            )
            filters_list += f", user_id:==:{uid}"
            try:
                filters_list = sqlalchemy_filters_converter(
                    Passwords,
                    filters_list
                )
            except Exception as error:
                return error.args[0]
            passwords = passwords.filter(*filters_list)
        if orders_list:
            try:
                orders_list = sqlalchemy_orders_converter(
                    Passwords, orders_list
                )
            except Exception as error:
                return error.args[0]
            passwords = passwords.order_by(*orders_list)
        # ----------------------------------------------------------------------

        passwords_dump = schema.dump(passwords)

        # Paginating results of dumping
        # Probably would best is pagination in sqlalchemy query?
        passwords_dump = pagination_of_list(
            passwords_dump,
            url_for(
                '.get_passwords',
                _external=True
            ),
            query_params=request.args
        )
        # ----------------------------------------------------------------------

        response = Response(
            response=json.dumps(passwords_dump),
            status=200,
            mimetype='application/json'
        )

    except Exception:

        response = json_http_response(dbg=request.args.get('dbg', False))

    return response
