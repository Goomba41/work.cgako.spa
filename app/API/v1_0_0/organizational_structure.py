"""Views of API version 1.0.0: User profile."""

from flask import Response, json, request, url_for

from .blueprint import APIv1_0_0
from app import db
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
        element_type = variable_type_check(request.args.get('type', 1), int)
        if not element_type.result:
            return json_http_response(
                status=400,
                given_message="Value «%s» from"
                " parameter «&type=%s» is not type of «%s»" % (
                    element_type.value,
                    element_type.value,
                    element_type.type
                ),
                dbg=request.args.get('dbg', False)
            )
        elif element_type.value not in range(1, 3, 1):
            return json_http_response(
                status=400,
                given_message="The type submitted in parameter"
                " «&type=%s» is does not exist" % (
                    element_type.value
                ),
                dbg=request.args.get('dbg', False)
            )

        parent_id = variable_type_check(request.args.get('parent', 1), int)
        if not parent_id.result:
            return json_http_response(
                status=400,
                given_message="Value «%s» from"
                " parameter «&parent=%s» is not type of «%s»" % (
                    parent_id.value,
                    parent_id.value,
                    parent_id.type
                ),
                dbg=request.args.get('dbg', False)
            )
        else:
            parent = OrganizationalStructure.query.filter(
                OrganizationalStructure.id == parent_id.value
            ).first()
            if not parent:
                return json_http_response(
                    status=400,
                    given_message="The parent submitted in parameter"
                    " «&parent=%s» is does not exist" % (
                        parent_id.value
                    ),
                    dbg=request.args.get('dbg', False)
                )

        name = variable_type_check(request.args.get('name'), str)
        if not name.result:
            return json_http_response(
                status=400,
                given_message="Value «%s» from"
                " parameter «&name=%s» is not type of «%s»" % (
                    name.value,
                    name.value,
                    name.type
                ),
                dbg=request.args.get('dbg', False)
            )
        if len(name.value) > 100:
            answer_string = str(
                name.value[:10]
            )+"..." if len(name.value) > 10 else name.value
            return json_http_response(
                status=400,
                given_message="Value «%s» from"
                " parameter «&name=%s» is out of range 1-100" % (
                    answer_string,
                    answer_string
                ),
                dbg=request.args.get('dbg', False)
            )
        elif len(name.value) <= 0:
            name = 'Должность' if element_type.value == 2 else (
                'Отдел' if (
                    element_type.value == 1 and parent_id.value == 1
                ) else 'Подотдел'
            )
        else:
            name = name.value

        if ((parent.type == 2 and element_type.value == 2) or
           (parent.type == 2 and element_type.value == 1)):
            return json_http_response(
                status=400,
                given_message="You cannot insert a new element"
                " «%s» under a position «%s»" % (
                    name,
                    parent.name,
                ),
                dbg=request.args.get('dbg', False)
            )
        else:
            node = OrganizationalStructure(
                parent_id=parent_id.value,
                type=element_type.value,
                name=name
            )
            db.session.add(node)
            db.session.flush()

            node_schema = OrganizationalStructureSchema(only=["name", "links"])
            node_dump = node_schema.dump(node)

            db.session.commit()

            output_json = {
                "message": "Successfully inserted element"
                " «%s» under a element «%s»" % (
                    name,
                    parent.name,
                ),
                "links": node_dump['links'],
                "responseType": "Success",
                "status": 200
            }

            response = Response(
                response=json.dumps(output_json),
                status=200,
                mimetype='application/json'
            )

    except Exception:

        response = json_http_response(dbg=request.args.get('dbg', False))

    return response


@APIv1_0_0.route('/organization/structure/elements/<int:id>', methods=['PUT'])
# @token_required
def put_organizational_structure_element(id):
    """Delete element from organizational structure."""
    try:
        response = Response(
            response=json.dumps("K.O.!"),
            status=200,
            mimetype='application/json'
        )
    except Exception:

        response = json_http_response(dbg=request.args.get('dbg', False))

    return response


@APIv1_0_0.route(
    '/organization/structure/elements/<int:id>',
    methods=['DELETE']
)
# @token_required
def delete_organizational_structure_element(id):
    """Delete element from organizational structure."""
    try:
        # node = OrganizationalStructure.query.filter
        #     OrganizationalStructure.id == 8
        # ).first()
        # db.session.delete(node)
        # db.session.commit()

        response = Response(
            response=json.dumps("K.O.!"),
            status=200,
            mimetype='application/json'
        )
    except Exception:

        response = json_http_response(dbg=request.args.get('dbg', False))

    return response
