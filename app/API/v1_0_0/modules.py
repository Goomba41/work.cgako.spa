"""Views of API version 1.0.0: User profile."""

from flask import request, Response, json, url_for
from flask_babel import _

from .blueprint import APIv1_0_0
from app.models import ModulesTypes, Modules
from app.schemas import ModulesTypesSchema, ModulesSchema
from .utils import json_http_response, marshmallow_excluding_converter, \
    marshmallow_only_fields_converter, sqlalchemy_filters_converter, \
    sqlalchemy_orders_converter, pagination_of_list


@APIv1_0_0.route('/modules/', methods=['GET'])
# @token_required
def get_modules():
    """Get modules list."""
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
                    Modules, exclusions_list
                )
                if 'id' in exclusions_list:
                    exclusions_list.remove('id')
                dump_params['exclude'] = exclusions_list
            if columns_list:
                columns_list = marshmallow_only_fields_converter(
                    Modules, columns_list
                )
                dump_params['only'] = ["id"] + columns_list
        except Exception as error:
            return error.args[0]

        schema = ModulesSchema(**dump_params)
        # ----------------------------------------------------------------------

        # Make empty base query and if
        # filters and orders exist - add it to query
        elements = Modules.query

        if filters_list:
            try:
                filters_list = sqlalchemy_filters_converter(
                    Modules,
                    filters_list
                )
            except Exception as error:
                return error.args[0]
            elements = elements.filter(*filters_list)
        if orders_list:
            try:
                orders_list = sqlalchemy_orders_converter(
                    Modules, orders_list
                )
            except Exception as error:
                return error.args[0]
            elements = elements.order_by(*orders_list)
        # ----------------------------------------------------------------------

        data = schema.dump(elements.all())

        # Paginating results of dumping
        # Probably would best is pagination in sqlalchemy query?
        data = pagination_of_list(
            data,
            url_for(
                '.get_modules',
                _external=True
            ),
            query_params=request.args
        )
        # ----------------------------------------------------------------------

        response = Response(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )
    except Exception:

        response = json_http_response(dbg=request.args.get('dbg', False))

    return response


@APIv1_0_0.route('/modules/<int:id>', methods=['GET'])
# @token_required
def get_modules_item(id):
    """Get modules item by id."""
    try:
        print(f"GET MODULE {id}")
        response = json_http_response(
            status=200,
            dbg=request.args.get('dbg', False)
        )
    except Exception:

        response = json_http_response(dbg=request.args.get('dbg', False))

    return response


@APIv1_0_0.route('/modules/types/', methods=['GET'])
# @token_required
def get_modules_types():
    """Get modules types list."""
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
                    ModulesTypes, exclusions_list
                )
                if 'id' in exclusions_list:
                    exclusions_list.remove('id')
                dump_params['exclude'] = exclusions_list
            if columns_list:
                columns_list = marshmallow_only_fields_converter(
                    ModulesTypes, columns_list
                )
                dump_params['only'] = ["id"] + columns_list
        except Exception as error:
            return error.args[0]

        schema = ModulesTypesSchema(**dump_params)
        # ----------------------------------------------------------------------

        # Make empty base query and if
        # filters and orders exist - add it to query
        elements = ModulesTypes.query

        if filters_list:
            try:
                filters_list = sqlalchemy_filters_converter(
                    ModulesTypes,
                    filters_list
                )
            except Exception as error:
                return error.args[0]
            elements = elements.filter(*filters_list)
        if orders_list:
            try:
                orders_list = sqlalchemy_orders_converter(
                    ModulesTypes, orders_list
                )
            except Exception as error:
                return error.args[0]
            elements = elements.order_by(*orders_list)
        # ----------------------------------------------------------------------

        data = schema.dump(elements.all())

        # Paginating results of dumping
        # Probably would best is pagination in sqlalchemy query?
        data = pagination_of_list(
            data,
            url_for(
                '.get_modules_types',
                _external=True
            ),
            query_params=request.args
        )
        # ----------------------------------------------------------------------

        response = Response(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )
    except Exception:

        response = json_http_response(dbg=request.args.get('dbg', False))

    return response


@APIv1_0_0.route('/modules/types/<int:id>', methods=['GET'])
# @token_required
def get_modules_types_item(id):
    """Get modules types item by id."""
    try:
        # Get parameters from request
        exclusions_list = request.args.get('exclude')
        columns_list = request.args.get('columns')

        # Forming dumping parameters
        dump_params = {}

        # Check if values of getted parameters exist in database table
        # and set dump settings
        try:
            if exclusions_list:
                exclusions_list = marshmallow_excluding_converter(
                    ModulesTypes, exclusions_list
                )
                if 'id' in exclusions_list:
                    exclusions_list.remove('id')
                dump_params['exclude'] = exclusions_list
            if columns_list:
                columns_list = marshmallow_only_fields_converter(
                    ModulesTypes, columns_list
                )
                dump_params['only'] = ["id"] + columns_list
        except Exception as error:
            return error.args[0]

        schema = ModulesTypesSchema(**dump_params)
        # ----------------------------------------------------------------------

        # Query item from database, and if is not none dump it
        item = ModulesTypes.query.get(id)
        if not item:
            return json_http_response(
                status=404,
                given_message=_(
                    "Module type with id=%(id)s doesn't exist in database",
                    id=id
                ),
                dbg=request.args.get('dbg', False)
            )

        data = schema.dump(item)
        # ----------------------------------------------------------------------

        response = Response(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )
    except Exception:

        response = json_http_response(dbg=request.args.get('dbg', False))

    return response


@APIv1_0_0.route('/modules/types/<int:id>', methods=['PUT'])
# @token_required
def put_modules_type_item(id):
    """Update module information."""
    try:
        print(f"PUT MODULE TYPE {id} INFORMATION")
        response = json_http_response(
            status=200,
            dbg=request.args.get('dbg', False)
        )
    except Exception:

        response = json_http_response(dbg=request.args.get('dbg', False))

    return response


@APIv1_0_0.route('/modules/<int:id>', methods=['PUT'])
# @token_required
def put_modules_item(id):
    """Update module information."""
    try:
        print(f"PUT MODULE {id} INFORMATION")
        response = json_http_response(
            status=200,
            dbg=request.args.get('dbg', False)
        )
    except Exception:

        response = json_http_response(dbg=request.args.get('dbg', False))

    return response
