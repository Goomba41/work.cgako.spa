"""Views of API version 1.0.0: User profile."""

from flask import Response, json, request, url_for
from flask_babel import _
from collections import Counter

from .blueprint import APIv1_0_0
from app import db
from app.models import OrganizationalStructure
from app.schemas import OrganizationalStructureSchema
from .utils import json_http_response, marshmallow_excluding_converter, \
    marshmallow_only_fields_converter, sqlalchemy_filters_converter, \
    sqlalchemy_orders_converter, pagination_of_list, variable_type_check


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
        # ----------------------------------------------------------------------

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
        # ----------------------------------------------------------------------

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
        # ----------------------------------------------------------------------

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
        # ----------------------------------------------------------------------

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
        # ----------------------------------------------------------------------

        # Query item from database, and if is not none make action
        item = OrganizationalStructure.query.get(id)
        if not item:

            return json_http_response(
                status=404,
                given_message=_(
                    "Element with id=%(id)s doesn't exist in database",
                    id=id
                ),
                dbg=request.args.get('dbg', False)
            )

        # Check variable type and if type is correct and value is True
        # return drilled element, else dump to json by schema
        check = variable_type_check(drilldown, bool)

        if check.result and check.value:
            item_json = item.drilldown_tree(
                json=True,
                json_fields=item_schema.dump
            )
        else:
            item_json = item_schema.dump(item)
        # ----------------------------------------------------------------------

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
        # Check element type (should be a number and 1-2 range)
        element_type = variable_type_check(request.args.get('type', 1), int)
        if not element_type.result:
            return json_http_response(
                status=400,
                given_message=_(
                    "Value «%(value)s» from parameter «&type=%(value)s»"
                    " is not type of «%(type)s»",
                    value=element_type.value,
                    type=element_type.type
                ),
                dbg=request.args.get('dbg', False)
            )
        elif element_type.value not in range(1, 3, 1):
            return json_http_response(
                status=400,
                given_message=_(
                    "The type submitted in parameter"
                    " «&type=%(value)s» is does not exist",
                    value=element_type.value,
                ),
                dbg=request.args.get('dbg', False)
            )
        # ----------------------------------------------------------------------
        # Check parent id (should be a number, this parent should be exsiting
        # in database and should be insertable; default is root element)
        parent_id = variable_type_check(request.args.get('parent', 1), int)
        if not parent_id.result:
            return json_http_response(
                status=400,
                given_message=_(
                    "Value «%(value)s» from parameter «&type=%(value)s»"
                    " is not type of «%(type)s»",
                    value=parent_id.value,
                    type=parent_id.type
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
                    given_message=_(
                        "The parent submitted in parameter"
                        " «&parent=%(value)s» is does not exist",
                        value=parent_id.value,
                    ),
                    dbg=request.args.get('dbg', False)
                )
            elif parent.type != 1 or not parent.insertable:
                return json_http_response(
                    status=403,
                    given_message=_(
                        "Element cannot be inserted into parent «%(name)s»"
                        " with id=%(value)s: parent is the position of the ,"
                        " department or insertion into the parent"
                        " is prohibited",
                        name=parent.name,
                        value=parent_id.value,
                    ),
                    dbg=request.args.get('dbg', False)
                )
        # ----------------------------------------------------------------------
        # Check name parameter (should be a string in range 1-100, default name
        # is choosen depending on type)
        name = variable_type_check(request.args.get('name', '').strip(), str)
        if not name.result:
            return json_http_response(
                status=400,
                given_message=_(
                    "Value «%(value)s» from parameter «&name=%(value)s»"
                    " is not type of «%(type)s»",
                    value=name.value,
                    type=name.type
                ),
                dbg=request.args.get('dbg', False)
            )
        if len(name.value) > 100:
            answer_string = str(
                name.value[:5]
            )+"..."+str(
                name.value[-5:]
            ) if len(
                name.value
            ) > 10 else name.value
            return json_http_response(
                status=400,
                given_message=_(
                    "Value «%(value)s» from parameter «&name=%(value)s»"
                    " is out of range 1-100",
                    value=answer_string
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
        # ----------------------------------------------------------------------
        # Get object state parameters from request and change if necessary
        # Check insertable state (boolean)
        element_insertable = variable_type_check(
            request.args.get('insertable', True),
            bool
        )
        if not element_insertable.result:
            return json_http_response(
                status=400,
                given_message=_(
                    "Value «%(value)s» from parameter «&insertable=%(value)s»"
                    " is not type of «%(type)s»",
                    value=element_insertable.value,
                    type=element_insertable.type
                ),
                dbg=request.args.get('dbg', False)
            )
        else:
            insertable = element_insertable.value
        # ----------------------------------------------------------------------
        # Check updatable state (boolean)
        element_updatable = variable_type_check(
            request.args.get('updatable', True),
            bool
        )
        if not element_updatable.result:
            return json_http_response(
                status=400,
                given_message=_(
                    "Value «%(value)s» from parameter «&updatable=%(value)s»"
                    " is not type of «%(type)s»",
                    value=element_updatable.value,
                    type=element_updatable.type
                ),
                dbg=request.args.get('dbg', False)
            )
        else:
            updatable = element_updatable.value
        # ----------------------------------------------------------------------
        # Check movable state (boolean)
        element_movable = variable_type_check(
            request.args.get('movable', True),
            bool
        )
        if not element_movable.result:
            return json_http_response(
                status=400,
                given_message=_(
                    "Value «%(value)s» from parameter «&movable=%(value)s»"
                    " is not type of «%(type)s»",
                    value=element_movable.value,
                    type=element_movable.type
                ),
                dbg=request.args.get('dbg', False)
            )
        else:
            movable = element_movable.value
        # ----------------------------------------------------------------------
        # Check deletable state (boolean)
        element_deletable = variable_type_check(
            request.args.get('deletable', True),
            bool
        )
        if not element_deletable.result:
            return json_http_response(
                status=400,
                given_message=_(
                    "Value «%(value)s» from parameter «&deletable=%(value)s»"
                    " is not type of «%(type)s»",
                    value=element_deletable.value,
                    type=element_deletable.type
                ),
                dbg=request.args.get('dbg', False)
            )
        else:
            deletable = element_deletable.value
        # ----------------------------------------------------------------------
        # Check parent type (if department position prohibit adding child node)
        if parent.type == 2:
            return json_http_response(
                status=400,
                given_message=_(
                    "You cannot insert a new element «%(name)s»"
                    " under a position «%(parent)s»",
                    name=name,
                    parent=parent.name
                ),
                dbg=request.args.get('dbg', False)
            )
        else:
            node = OrganizationalStructure(
                parent_id=parent_id.value,
                type=element_type.value,
                name=name,
                insertable=insertable,
                deletable=deletable,
                movable=movable,
                updatable=updatable,
            )
            db.session.add(node)
            db.session.flush()

            # Before send response, dump newly added element to json and add
            # his data to response
            node_schema = OrganizationalStructureSchema(
                only=["id", "name", "links", "type"]
            )
            node_dump = node_schema.dump(node)
            db.session.commit()

            output_json = {
                "message": _(
                    "Successfully inserted element «%(name)s»"
                    " under a element «%(parent)s»",
                    name=name,
                    parent=parent.name
                ),
                "node": node_dump,
                "responseType": _("Success"),
                "status": 200
            }
            # ------------------------------------------------------------------

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

        # Check element to be deleted (deletable parameter should be True,
        # element is not root, and exist)
        node_to_delete = OrganizationalStructure.query.filter(
            OrganizationalStructure.id == id
        ).first()

        if not node_to_delete.deletable:
            return json_http_response(
                status=403,
                given_message=_(
                    "Element «%(name)s» with id=%(id)s is prohibited from"
                    " deleting",
                    name=node_to_delete.name,
                    id=node_to_delete.id
                ),
                dbg=request.args.get('dbg', False)
            )

        if node_to_delete is None:
            return json_http_response(
                status=404,
                given_message=_(
                    "Element to delete with id=%(value)s"
                    " is not exist in database",
                    value=id
                ),
                dbg=request.args.get('dbg', False)
            )
        elif node_to_delete.id == 1 or node_to_delete.left == 1:
            return json_http_response(
                status=400,
                given_message=_(
                    "Root element «%(name)s»"
                    " cannot be deleted",
                    name=node_to_delete.name
                ),
                dbg=request.args.get('dbg', False)
            )
        # ----------------------------------------------------------------------
        # Check recursive parameter (should be a boolean)
        recursive = variable_type_check(
            request.args.get('recursive', False), bool
        )
        if not recursive.result:
            return json_http_response(
                status=400,
                given_message=_(
                    "Value «%(value)s» from parameter «&recursive=%(value)s»"
                    " is not type of «%(type)s»",
                    value=recursive.value,
                    type=recursive.type
                ),
                dbg=request.args.get('dbg', False)
            )
        # If recursive is True, delete element with his child nodes, else move
        # child nodes to parent of deleted element
        elif recursive.value:
            if len(node_to_delete.children):
                given_message = _(
                    "Element «%(name)s» successfully deleted from"
                    " database with all children elements",
                    name=node_to_delete.name
                )
                for child in node_to_delete.children:
                    if not child.deletable:
                        child.move_inside(node_to_delete.parent_id)
                        db.session.commit()
                        given_message = _(
                            "Element «%(name)s» successfully deleted from"
                            " database with all children elements."
                            " Non deletable childs moved to top level.",
                            name=node_to_delete.name
                        )
            else:
                given_message = _(
                    "Element «%(name)s» successfully deleted from"
                    " database",
                    name=node_to_delete.name
                )
            db.session.delete(node_to_delete)
        else:
            if len(node_to_delete.children):
                # Moving child to parent of root element
                # to prevent from deletion
                for child in node_to_delete.children:
                    child.move_inside(node_to_delete.parent_id)
                db.session.commit()

                # And then delete root element
                db.session.delete(node_to_delete)
                given_message = _(
                    "Element «%(name)s» successfully deleted from"
                    " database. All children elements moved to top level",
                    name=node_to_delete.name
                )
            else:
                db.session.delete(node_to_delete)
                given_message = _(
                    "Element «%(name)s» successfully deleted from"
                    " database",
                    name=node_to_delete.name
                )
        # ----------------------------------------------------------------------

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
    # Inner function for element checkings and moving
    def elements_moving(id, move_type):
        # Check id of moved element (should be a number), and if passed check
        # element parent
        id = variable_type_check(id, int)
        if not id.result:
            return json_http_response(
                status=400,
                given_message=_(
                    "Value «%(value)s» from parameter «&parent=%(value)s»"
                    " is not type of «%(type)s»",
                    value=id.value,
                    type=id.type
                ),
                dbg=request.args.get('dbg', False)
            )
        else:
            # Get target element
            target = OrganizationalStructure.query.filter(
                OrganizationalStructure.id == id.value
            ).first()
            # -
            if not target:
                raise Exception(json_http_response(
                    status=404,
                    given_message=_(
                        "The target in one of submitted parameter"
                        " «&parent», «&before», «&after» is does not exist"
                    ),
                    dbg=request.args.get('dbg', False)
                ))
            # If element exist check type and move element
            elif move_type == 'inside' and (
                        target.type == 2 or not target.insertable
                    ):
                raise Exception(json_http_response(
                    status=403,
                    given_message=_(
                        "Unable to move element with id=%(id)s to element"
                        " with id=%(target_id)s: target element is of type 2"
                        " (department position cannot have children)"
                        " or insertion into target item is not allowed",
                        id=node_to_update.id,
                        target_id=target.id
                    ),
                    dbg=request.args.get('dbg', False)
                ))
            # If move type inside and target element not type of 2
            # and insertable, move inside target
            elif move_type == 'inside' and (
                node_to_update.parent_id != id.value
            ):
                node_to_update.move_inside(id.value)
            # Else if move type is after or before and parent of target
            # is insertable, move element
            elif target.parent.insertable:
                if move_type == 'after':
                    node_to_update.move_after(id.value)
                if move_type == 'before':
                    node_to_update.move_before(id.value)
            else:
                raise Exception(json_http_response(
                    status=403,
                    given_message=_(
                        "Unable to move element with id=%(id)s before or"
                        " after element with id=%(target_id)s: insertion into"
                        " target element parent with id=%(target_parent_id)s"
                        " is not allowed",
                        id=node_to_update.id,
                        target_id=target.id,
                        target_parent_id=target.parent.id
                    ),
                    dbg=request.args.get('dbg', False)
                ))
            # ------------------------------------------------------------------
        # ----------------------------------------------------------------------

    try:
        # Check if asked element is exist and he is not root element
        node_to_update = OrganizationalStructure.query.filter(
            OrganizationalStructure.id == id
        ).first()

        if node_to_update is None:
            return json_http_response(
                status=404,
                given_message=_(
                    "Element to update with id=%(id)s is not exist"
                    " in database",
                    id=id
                ),
                dbg=request.args.get('dbg', False)
            )
        elif node_to_update.id == 1 or node_to_update.left == 1:
            return json_http_response(
                status=400,
                given_message=_(
                    "Root element «%(name)s» cannot be updated",
                    name=node_to_update.name
                ),
                dbg=request.args.get('dbg', False)
            )
        else:
            old_node_name = node_to_update.name
        # ----------------------------------------------------------------------
        # Get parameters from request and change if necessary
        element_type = request.args.get('type', None)
        element_name = request.args.get('name', None)
        # ----------------------------------------------------------------------

        # Get object state parameters from request and change if necessary
        element_deletable = request.args.get('deletable', None)
        element_movable = request.args.get('movable', None)
        element_updatable = request.args.get('updatable', None)
        element_insertable = request.args.get('insertable', None)
        # ----------------------------------------------------------------------
        # Check insertable parameter (should be a boolean) and toggle
        # if necessary
        if element_insertable:
            element_insertable = variable_type_check(element_insertable, bool)
            if not element_insertable.result:
                return json_http_response(
                    status=400,
                    given_message=_(
                        "Value «%(value)s» from parameter"
                        " «&insertable=%(value)s» is not type of «%(type)s»",
                        value=element_insertable.value,
                        type=element_insertable.type
                    ),
                    dbg=request.args.get('dbg', False)
                )
            elif node_to_update.insertable != element_insertable.value:
                node_to_update.insertable = element_insertable.value
        # ----------------------------------------------------------------------
        # Check updatable parameter (should be a boolean) and toggle
        # if necessary
        if element_updatable:
            element_updatable = variable_type_check(element_updatable, bool)
            if not element_updatable.result:
                return json_http_response(
                    status=400,
                    given_message=_(
                        "Value «%(value)s» from parameter"
                        " «&updatable=%(value)s» is not type of «%(type)s»",
                        value=element_updatable.value,
                        type=element_updatable.type
                    ),
                    dbg=request.args.get('dbg', False)
                )
            elif node_to_update.updatable != element_updatable.value:
                node_to_update.updatable = element_updatable.value
        # Check movable parameter (should be a boolean) and toggle
        # if necessary
        if element_movable:
            element_movable = variable_type_check(element_movable, bool)
            if not element_movable.result:
                return json_http_response(
                    status=400,
                    given_message=_(
                        "Value «%(value)s» from parameter «&movable=%(value)s»"
                        " is not type of «%(type)s»",
                        value=element_movable.value,
                        type=element_movable.type
                    ),
                    dbg=request.args.get('dbg', False)
                )
            elif node_to_update.movable != element_movable.value:
                node_to_update.movable = element_movable.value
        # Check deletable parameter (should be a boolean) and toggle
        # if necessary
        if element_deletable:
            element_deletable = variable_type_check(element_deletable, bool)
            if not element_deletable.result:
                return json_http_response(
                    status=400,
                    given_message=_(
                        "Value «%(value)s» from parameter"
                        " «&deletable=%(value)s» is not type of «%(type)s»",
                        value=element_deletable.value,
                        type=element_deletable.type
                    ),
                    dbg=request.args.get('dbg', False)
                )
            elif node_to_update.deletable != element_deletable.value:
                node_to_update.deletable = element_deletable.value
        # ----------------------------------------------------------------------

        # If request has type and name parameters and node is updatable
        # check parameters and update if necessary
        if (element_type or element_name) and node_to_update.updatable:
            # Check element type (should be a number in 1-2 range)
            if element_type:
                element_type = variable_type_check(element_type, int)
                if not element_type.result:
                    return json_http_response(
                        status=400,
                        given_message=_(
                            "Value «%(value)s» from parameter"
                            " «&type=%(value)s» is not type of «%(type)s»",
                            value=element_type.value,
                            type=element_type.type
                        ),
                        dbg=request.args.get('dbg', False)
                    )
                elif element_type.value not in range(1, 3, 1):
                    return json_http_response(
                        status=400,
                        given_message=_(
                            "The type submitted in parameter"
                            " «&type=%(value)s» is does not exist",
                            value=element_type.value
                        ),
                        dbg=request.args.get('dbg', False)
                    )
                elif element_type.value != node_to_update.type:
                    if len(node_to_update.children):
                        return json_http_response(
                            status=400,
                            given_message=_(
                                "Cannot change type of element with"
                                " id=%(id)s to type 2 (department position)"
                                "because he has child elements. Move child"
                                "elements under other element first.",
                                id=node_to_update.id
                            ),
                            dbg=request.args.get('dbg', False)
                        )
                    else:
                        node_to_update.type = element_type.value
            # ------------------------------------------------------------------
            # Check element name (should be a string in 1-100 range)
            if element_name:
                element_name = variable_type_check(element_name.strip(), str)
                if not element_name.result:
                    return json_http_response(
                        status=400,
                        given_message=_(
                            "Value «%(value)s» from parameter"
                            " «&name=%(value)s» is not type of «%(type)s»",
                            value=element_name.value,
                            type=element_name.type
                        ),
                        dbg=request.args.get('dbg', False)
                    )
                if len(element_name.value) > 100:
                    answer_string = str(
                        element_name.value[:5]
                    )+"..."+str(
                        element_name.value[-5:]
                    ) if len(
                        element_name.value
                    ) > 10 else element_name.value
                    return json_http_response(
                        status=400,
                        given_message=_(
                            "Value «%(value)s» from parameter"
                            " «&name=%(value)s» is out of range 1-100",
                            value=answer_string
                        ),
                        dbg=request.args.get('dbg', False)
                    )
                elif (len(element_name.value) > 0) and (
                        element_name.value != node_to_update.name
                ):
                    node_to_update.name = element_name.value
            # ------------------------------------------------------------------

        # Get parameters for moving element in the tree
        parent_id = request.args.get('parent', None)
        after_id = request.args.get('after', None)
        before_id = request.args.get('before', None)

        # Check if more than one parameter sending
        list1 = [
            True if x else False for x in (parent_id, after_id, before_id)
        ]

        test = dict(Counter(list1).items())

        if True in test.keys():
            # If one parameter sended, check if element movable
            if test[True] >= 1 and not node_to_update.movable:
                return json_http_response(
                    status=403,
                    given_message=_(
                        "Element «%(name)s» with id=%(id)s is prohibited"
                        " from moving to another elements",
                        name=node_to_update.name,
                        id=node_to_update.id
                    ),
                    dbg=request.args.get('dbg', False)
                )
            # ------------------------------------------------------------------
            # Else if more than or exactly 2 parameters sended, send a error
            elif test[True] >= 2:
                return json_http_response(
                    status=400,
                    given_message=_(
                        "Submitted more than one from parameters: parent,"
                        "after, before. May be processed only one parameter"
                        "at time. Please, exclude unnecessary parameters"
                        "from request first."
                    ),
                    dbg=request.args.get('dbg', False)
                )
            # ------------------------------------------------------------------
        # ----------------------------------------------------------------------
        # Try move element with inner function
        try:
            if parent_id:
                elements_moving(parent_id, 'inside')
            if after_id:
                # HAS MPTT LIBRARY BUG:
                # MOVING TOO FAR LEFT
                # https://github.com/uralbash/sqlalchemy_mptt/issues/67
                # elements_moving(after_id, 'after')
                return json_http_response(
                    status=400,
                    given_message=_(
                        "Function is bugged, so temporarly does not work"
                    ),
                    dbg=request.args.get('dbg', False)
                )
            if before_id:
                # HAS MPTT LIBRARY BUG:
                # AFTER MOVE ON LEFTMOST POSITION NOTHING HAPPEND
                # https://github.com/uralbash/sqlalchemy_mptt/issues/68
                elements_moving(before_id, 'before')
        except Exception as error:
            return error.args[0]
        # ----------------------------------------------------------------------

        # If session has changes then commit it form output message
        if db.session.dirty:
            db.session.commit()

            node_schema = OrganizationalStructureSchema()
            node_dump = node_schema.dump(node_to_update)

            output_json = {
                "message": _(
                    "Successfully updated element «%(name)s»",
                    name=old_node_name
                ),
                "node": node_dump,
                "responseType": _("Success"),
                "status": 200
            }
        # Else just form output message
        else:

            node_schema = OrganizationalStructureSchema()
            node_dump = node_schema.dump(node_to_update)

            output_json = {
                "message": _(
                    "Element «%(name)s» is stay unchanged by one of the"
                    " reasons: 1. you did not submit data 2. submitted data is"
                    " the same as old 3. element information update is not"
                    " allowed",
                    name=old_node_name
                ),
                "links": node_dump['links'],
                "responseType": _("Info"),
                "status": 304
            }
        # ----------------------------------------------------------------------

        response = Response(
            response=json.dumps(output_json),
            status=200,
            mimetype='application/json'
        )
    except Exception:

        response = json_http_response(dbg=request.args.get('dbg', False))

    return response
