"""Views of API version 1.0.0: User profile."""

from flask import Response, json, request, url_for
from collections import Counter

from .blueprint import APIv1_0_0
from app import db
from app.models import OrganizationalStructure
from app.schemas import OrganizationalStructureSchema
from .utils import json_http_response, marshmallow_excluding_converter, \
    marshmallow_only_fields_converter, sqlalchemy_filters_converter, \
    sqlalchemy_orders_converter, pagination_of_list, variable_type_check

# List of routes:
# PUT data to element or move him on tree


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
    """Post element to organizational structure.

    Post element to parent element by parent, name and type parameters.
    Type parameter is number 1 (department) or 2 (position of department).
    If parent is not sended, post element to root element. If name is not
    sended, set by default relative to type. Elements with any type cannot be
    inserted to element with type 2.
    """
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
                given_message="The type submitted parameter"
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
                    status=404,
                    given_message="The parent submitted parameter"
                    " «&parent=%s» is does not exist" % (
                        parent_id.value
                    ),
                    dbg=request.args.get('dbg', False)
                )

        name = variable_type_check(request.args.get('name', '').strip(), str)
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

            node_schema = OrganizationalStructureSchema(
                only=["id", "name", "links", "type"]
            )
            node_dump = node_schema.dump(node)

            db.session.commit()

            output_json = {
                "message": "Successfully inserted element"
                " «%s» under a element «%s»" % (
                    name,
                    parent.name,
                ),
                "links": node_dump['links'],
                "id": node_dump['id'],
                "type": node_dump['type'],
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


@APIv1_0_0.route(
    '/organization/structure/elements/<int:id>',
    methods=['DELETE']
)
# @token_required
def delete_organizational_structure_element(id):
    """Delete element from organizational structure.

    Delete element with recursion function (with all child elements)
    by boolean parameter. If parameter is False or not set, move all
    child elements to parent of deleting element, before delete element
    to prevent child deletion. 'Save' cascade deletion (to all users with
    position from this tree set NULL as 'company_position' foreign key). Checks
    for deletion element existense and is he the root element.
    """
    try:

        node_to_delete = OrganizationalStructure.query.filter(
            OrganizationalStructure.id == id
        ).first()

        if node_to_delete is None:
            return json_http_response(
                status=404,
                given_message="Element to delete with id=%s is not exist"
                " in database" % (id),
                dbg=request.args.get('dbg', False)
            )
        elif node_to_delete.id == 1 or node_to_delete.left == 1:
            return json_http_response(
                status=400,
                given_message="Root element «%s» cannot be deleted" % (
                    node_to_delete.name
                ),
                dbg=request.args.get('dbg', False)
            )

        recursive = variable_type_check(
            request.args.get('recursive', False), bool
        )
        if not recursive.result:
            return json_http_response(
                status=400,
                given_message="Value «%s» from"
                " parameter «&recursive=%s» is not type of «%s»" % (
                    recursive.value,
                    recursive.value,
                    recursive.type
                ),
                dbg=request.args.get('dbg', False)
            )
        elif recursive.value:
            db.session.delete(node_to_delete)

            if len(node_to_delete.children):
                given_message = "Element «{0}» successfully deleted from" \
                    " database with all children elements".format(
                        node_to_delete.name
                    )
            else:
                given_message = "Element «{0}» successfully deleted from" \
                    " database".format(
                        node_to_delete.name
                    )
        else:
            if len(node_to_delete.children):
                # Moving child to parent of root element
                # to prevent from deletion
                for child in node_to_delete.children:
                    child.move_inside(node_to_delete.parent_id)
                db.session.commit()

                # And then delete root element
                db.session.delete(node_to_delete)
                given_message = "Element «{0}» successfully deleted from" \
                    " database. All children elements moved to top" \
                    " level".format(
                        node_to_delete.name
                    )
            else:
                db.session.delete(node_to_delete)
                given_message = "Element «{0}» successfully deleted from" \
                    " database".format(
                        node_to_delete.name
                    )

        db.session.commit()

        return json_http_response(
            status=200,
            given_message=given_message,
            dbg=request.args.get('dbg', False)
        )
    except Exception:

        response = json_http_response(dbg=request.args.get('dbg', False))

    return response


@APIv1_0_0.route('/organization/structure/elements/<int:id>', methods=['PUT'])
# @token_required
def put_organizational_structure_element(id):
    """Change info, parent, order of element from organizational structure.

    Update info about element by data fields (name, type) and parameters
    'after' and 'before'. Before and after parameters cannot be used at the
    same time. When changing element type, check its children, and if there
    are, then element cannot be of type 2 (department position). Cannot be
    inserted into type 2 element.
    """
    def elements_moving(id, move_type):
        id = variable_type_check(id, int)
        if not id.result:
            return json_http_response(
                status=400,
                given_message="Value «%s» from"
                " parameter «&parent=%s» is not type of «%s»" % (
                    id.value,
                    id.value,
                    id.type
                ),
                dbg=request.args.get('dbg', False)
            )
        else:
            target = OrganizationalStructure.query.filter(
                OrganizationalStructure.id == id.value
            ).first()
            if not target:
                raise Exception(json_http_response(
                    status=404,
                    given_message="The target in one of submitted parameter"
                    " «&parent=», «&before=», «&after=» is does not exist" % (
                        id.value
                    ),
                    dbg=request.args.get('dbg', False)
                ))
            elif move_type == 'inside' and target.type == 2:
                raise Exception(json_http_response(
                    status=400,
                    given_message="Cannot move element with"
                    " id=%s to type 2 (department position) element."
                    " Position cannot have child elements." % (
                        node_to_update.id
                    ),
                    dbg=request.args.get('dbg', False)
                ))
            elif move_type == 'inside' and (
                node_to_update.parent_id != id.value
            ):
                node_to_update.move_inside(id.value)
                print("move inside %s" % id.value)
            else:
                if move_type == 'after':
                    node_to_update.move_after(id.value)
                    print("move after %s" % id.value)
                if move_type == 'before':
                    print(node_to_update.left, node_to_update.right, node_to_update.parent_id)
                    node_to_update.move_before(id.value)
                    print("%s move before %s" % (node_to_update.id, id.value))
                    print(node_to_update.left, node_to_update.right, node_to_update.parent_id)

    try:
        # Check if asked element is exist and he is not root element
        node_to_update = OrganizationalStructure.query.filter(
            OrganizationalStructure.id == id
        ).first()
        old_node_name = node_to_update.name

        if node_to_update is None:
            return json_http_response(
                status=404,
                given_message="Element to update with id=%s is not exist"
                " in database" % (id),
                dbg=request.args.get('dbg', False)
            )
        elif node_to_update.id == 1 or node_to_update.left == 1:
            return json_http_response(
                status=400,
                given_message="Root element «%s» cannot be updated" % (
                    node_to_update.name
                ),
                dbg=request.args.get('dbg', False)
            )

        # Get parameters from request and change if needed
        element_type = request.args.get('type', None)
        if element_type:
            element_type = variable_type_check(element_type, int)
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
                    given_message="The type submitted parameter"
                    " «&type=%s» is does not exist" % (
                        element_type.value
                    ),
                    dbg=request.args.get('dbg', False)
                )
            elif element_type.value != node_to_update.type:
                if len(node_to_update.children):
                    return json_http_response(
                        status=400,
                        given_message="Cannot change type of element with"
                        " id=%s to type 2 (department position) because he"
                        " has child elements. Move child elements under"
                        " other element first." % (node_to_update.id),
                        dbg=request.args.get('dbg', False)
                    )
                else:
                    node_to_update.type = element_type.value

        element_name = request.args.get('name', None)
        if element_name:
            element_name = variable_type_check(element_name.strip(), str)
            if not element_name.result:
                return json_http_response(
                    status=400,
                    given_message="Value «%s» from"
                    " parameter «&name=%s» is not type of «%s»" % (
                        element_name.value,
                        element_name.value,
                        element_name.type
                    ),
                    dbg=request.args.get('dbg', False)
                )
            if len(element_name.value) > 100:
                answer_string = str(
                    element_name.value[:10]
                )+"..." if len(element_name.value) > 10 else element_name.value
                return json_http_response(
                    status=400,
                    given_message="Value «%s» from"
                    " parameter «&name=%s» is out of range 1-100" % (
                        answer_string,
                        answer_string
                    ),
                    dbg=request.args.get('dbg', False)
                )
            elif (len(element_name.value) > 0) and (
                    element_name.value != node_to_update.name
            ):
                node_to_update.name = element_name.value

        parent_id = request.args.get('parent', None)
        after_id = request.args.get('after', None)
        before_id = request.args.get('before', None)

        list1 = [
            True if x else False for x in (parent_id, after_id, before_id)
        ]

        if dict(Counter(list1).items())[True] >= 2:
            return json_http_response(
                status=400,
                given_message="Submitted more than one from parameters:"
                " parent, after, before. May be processed only one parameter"
                " at time. Please, exclude unnecessary parameterы from request"
                " first.",
                dbg=request.args.get('dbg', False)
            )

        try:
            if parent_id:
                elements_moving(parent_id, 'inside')
            if after_id:
                # ЗДЕСЬ ЕСТЬ БАГ В БИБЛИОТЕКЕ MPTT:
                # СМЕЩАЕТСЯ НА ОДИН БОЛЬШЕ
                # https://github.com/uralbash/sqlalchemy_mptt/issues/67
                # elements_moving(after_id, 'after')
                return json_http_response(
                    status=400,
                    given_message="Function is bugged, so temporarly does"
                    " not work",
                    dbg=request.args.get('dbg', False)
                )
            if before_id:
                # ЗДЕСЬ ЕСТЬ БАГ В БИБЛИОТЕКЕ MPTT:
                # ПРИ ПЕРЕМЕЩЕНИИ НА САМУЮ ЛЕВУЮ ПОЗИЦИЮ НИЧЕГО НЕ ПРОИСХОДИТ
                # https://github.com/uralbash/sqlalchemy_mptt/issues/68
                elements_moving(before_id, 'before')
        except Exception as error:
            return error.args[0]

        node_schema = OrganizationalStructureSchema(only=["name", "links"])
        node_dump = node_schema.dump(node_to_update)

        if db.session.dirty:
            db.session.commit()

            output_json = {
                "message": "Successfully updated element"
                " «%s»" % (old_node_name),
                "links": node_dump['links'],
                "responseType": "Success",
                "status": 200
            }
        else:
            output_json = {
                "message": "Element «%s» is stay unchanged, because you"
                " did not submit data or submitted data is the same" % (
                    old_node_name
                ),
                "links": node_dump['links'],
                "responseType": "Success",
                "status": 304
            }

        response = Response(
            response=json.dumps(output_json),
            status=200,
            mimetype='application/json'
        )
    except Exception:

        response = json_http_response(dbg=request.args.get('dbg', False))

    return response
