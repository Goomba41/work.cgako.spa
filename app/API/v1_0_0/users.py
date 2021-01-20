"""Views of API version 1.0.0: Users."""

from flask import Response, json, request, url_for

from app.API.v1_0_0.blueprint import APIv1_0_0
from app.models import Users
from app.schema import UsersSchema
from .utils import json_http_response, sqlalchemy_filters_converter,\
    sqlalchemy_orders_converter, pagination_of_list,\
    marshmallow_excluding_converter, marshmallow_only_fields_converter

# List of routes:
# * GET ALL users
# * GET ONE user
# POST user
# PUT user
# DELETE user
# POST user avatar
# PUT user avatar ?
# DELETE user avatar


@APIv1_0_0.route('/users', methods=['GET'])
# @token_required
def get_users():
    """Get paginated users list."""
    try:
        # Get filters, order by and exclusions lists from request
        filter_parameters = request.args.getlist('filter')
        order_parameters = request.args.getlist('order_by')
        exclusions_list = request.args.getlist('exclude')
        columns_list = request.args.getlist('column')

        exclusions_default = [
            'roles.users',
            'departments_positions.users',
            'departments.users',
        ]

        # Check if getted parameters exist in database table
        try:
            filters_list = sqlalchemy_filters_converter(
                Users,
                filter_parameters
            )
            orders_list = sqlalchemy_orders_converter(
                Users,
                order_parameters
            )
            exclusions_list = marshmallow_excluding_converter(
                Users, exclusions_list
            )
            columns_list = marshmallow_only_fields_converter(
                Users, columns_list
            )
        # Catching exception from child function and getting its parameter
        # (response in this case)
        except Exception as error:
            return error.args[0]

        # Forming dumping parameters
        dump_params = {}

        if exclusions_list:
            if 'id' in exclusions_list:
                exclusions_list.remove('id')
            dump_params['exclude'] = exclusions_list + exclusions_default

        if columns_list:
            dump_params['only'] = ["id"] + columns_list

        # Querying database with filters and ordering lists
        users = Users.query.filter(*filters_list).order_by(*orders_list).all()
        # And dumping it to json by schema
        users_schema = UsersSchema(
            many=True,
            **dump_params
        )

        users_json = users_schema.dump(users)

        # Paginating results of dumping
        # Probably would best is pagination in sqlalchemy query?
        paginated_data = pagination_of_list(
            users_json,
            url_for(
                '.get_users',
                _external=True
            ),
            query_params=request.args
        )

        response = Response(
            response=json.dumps(paginated_data),
            status=200,
            mimetype='application/json'
        )

        return response

    except Exception:

        return json_http_response(dbg=request.args.get('dbg', False))


@APIv1_0_0.route('/users/<int:id>', methods=['GET'])
# @token_required
def get_user(id):
    """Get one users by id."""
    try:
        # Get a list of excluded fields and only fields from a dump
        exclusions_list = request.args.getlist('exclude')
        columns_list = request.args.getlist('column')

        exclusions_default = [
            'roles.users',
            'departments_positions.users',
            'departments.users',
        ]

        # Check if getted parameters exist in database table
        try:
            exclusions_list = marshmallow_excluding_converter(
                Users, exclusions_list
            )
            columns_list = marshmallow_only_fields_converter(
                Users, columns_list
            )
        except Exception as error:
            return error.args[0]

        # Forming dumping parameters
        dump_params = {}

        if exclusions_list:
            if 'id' in exclusions_list:
                exclusions_list.remove('id')
            dump_params['exclude'] = exclusions_list + exclusions_default

        if columns_list:
            dump_params['only'] = ["id"] + columns_list

        # Querying database for entity by id
        user = Users.query.get(id)
        # And dumping it to json by schema
        # (with the addition of excluded and only fields)
        user_schema = UsersSchema(**dump_params)

        user_json = user_schema.dump(user)

        response = Response(
            response=json.dumps(user_json),
            status=200,
            mimetype='application/json'
        )

        return response

    except Exception:

        return json_http_response(dbg=request.args.get('dbg', False))
