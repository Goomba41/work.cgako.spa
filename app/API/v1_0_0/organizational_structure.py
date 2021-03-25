"""Views of API version 1.0.0: User profile."""

from flask import Response, json, request, url_for

from .blueprint import APIv1_0_0
from app.models import OrganizationalStructure
from app.schemas import OrganizationalStructureSchema
from .utils import json_http_response, marshmallow_excluding_converter, \
    marshmallow_only_fields_converter, sqlalchemy_filters_converter, \
    sqlalchemy_orders_converter, pagination_of_list, variable_type_check

# List of routes:
# GET full tree
# GET part of tree
# POST element to tree
# PUT data to element or move him on tree
# DELETE element of tree


@APIv1_0_0.route('/organization/structure', methods=['GET'])
@APIv1_0_0.route('/organization/structure/elements', methods=['GET'])
# @token_required
def get_organizational_structure():
    """Get organizational structure tree."""
    try:
        # Get parameters from request
        filters_list = request.args.get('filters')
        exclusions_list = request.args.get('exclude')
        columns_list = request.args.get('columns')
        orders_list = request.args.get('order_by')

        # Forming dumping parameters
        dump_params = {}

        # Check if values of getted parameters exist in database table
        # and set dump settings
        try:
            if filters_list:
                filters_list = sqlalchemy_filters_converter(
                    OrganizationalStructure,
                    filters_list
                )
                dump_params['many'] = True
            if exclusions_list:
                exclusions_list = marshmallow_excluding_converter(
                    OrganizationalStructure, exclusions_list
                )
                if 'id' in exclusions_list:
                    exclusions_list.remove('id')
                dump_params['exclude'] = exclusions_list
            if columns_list:
                columns_list = marshmallow_only_fields_converter(
                    OrganizationalStructure, columns_list
                )
                dump_params['only'] = ["id"] + columns_list
        except Exception as error:
            return error.args[0]

        schema = OrganizationalStructureSchema(**dump_params)

        # If request has filters, then we request individual instances
        # of elements from database without nesting,
        # else drilldown tree with nested elements
        if filters_list:
            orders_list = sqlalchemy_orders_converter(
                OrganizationalStructure, orders_list
            )
            elements = OrganizationalStructure.query.filter(
                *filters_list
            ).order_by(*orders_list).all()
            tree = schema.dump(elements)

            # Paginating results of dumping
            # Probably would best is pagination in sqlalchemy query?
            tree = pagination_of_list(
                tree,
                url_for(
                    '.get_organizational_structure',
                    _external=True
                ),
                query_params=request.args
            )
        else:
            root_element = OrganizationalStructure.query.get(1)
            tree = root_element.drilldown_tree(
                json=True,
                json_fields=schema.dump
            )

        response = Response(
            response=json.dumps(tree),
            status=200,
            mimetype='application/json'
        )

    except Exception:

        response = json_http_response(dbg=request.args.get('dbg', False))

    return response


@APIv1_0_0.route('/organization/structure/elements/<int:id>', methods=['GET'])
# @token_required
def get_organizational_structure_element(id):
    """Get organizational structure element."""
    try:
        # Get parameters from request
        exclusions_list = request.args.get('exclude')
        columns_list = request.args.get('columns')
        drilldown = request.args.get('drilldown', False)

        # Forming dumping parameters
        dump_params = {}

        # Check if values of getted parameters exist in database table
        # and set dump settings
        try:
            if exclusions_list:
                exclusions_list = marshmallow_excluding_converter(
                    OrganizationalStructure, exclusions_list
                )
                if 'id' in exclusions_list:
                    exclusions_list.remove('id')
                dump_params['exclude'] = exclusions_list
            if columns_list:
                columns_list = marshmallow_only_fields_converter(
                    OrganizationalStructure, columns_list
                )
                dump_params['only'] = ["id"] + columns_list
        except Exception as error:
            return error.args[0]

        # Make schema with dumping parameters
        item_schema = OrganizationalStructureSchema(**dump_params)

        # Querying database for entity by id
        item = OrganizationalStructure.query.get(id)

        # Check variable type
        check = variable_type_check(drilldown, bool)

        # If type is correct and value is true
        if check.result and check.value:
            # Return drilled element
            item_json = item.drilldown_tree(
                json=True,
                json_fields=item_schema.dump
            )
        else:
            # Else dumping it to json by schema
            item_json = item_schema.dump(item)

        response = Response(
            response=json.dumps(item_json),
            status=200,
            mimetype='application/json'
        )

    except Exception:

        response = json_http_response(dbg=request.args.get('dbg', False))

    return response


@APIv1_0_0.route('/organization/structure/elements/', methods=['POST'])
# @token_required
def post_organizational_structure_element():
    """Post element to organizational structure."""
    try:
        # Get parameters from request
        element_type = request.args.get('type', 1)
        parent_id = request.args.get('parent', 1)
        name = request.args.get('name', False)

        print(element_type, parent_id, name)

        response = Response(
            response=json.dumps("K.O.!"),
            status=200,
            mimetype='application/json'
        )
    except Exception:

        response = json_http_response(dbg=request.args.get('dbg', False))

    return response
