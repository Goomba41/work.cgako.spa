"""Views of API version 1.0.0: System modules and modules types."""

import re

from flask import request, Response, json, url_for
from flask_babel import _
from app import db

from .blueprint import APIv1_0_0
from app.models import ModulesTypes, Modules
from app.schemas import ModulesTypesSchema, ModulesSchema
from .utils import json_http_response, marshmallow_excluding_converter, \
    marshmallow_only_fields_converter, sqlalchemy_filters_converter, \
    sqlalchemy_orders_converter, pagination_of_list, variable_type_check


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


@APIv1_0_0.route('/modules/<int:id>', methods=['PUT'])
# @token_required
def put_modules_item(id):
    """Update module information."""
    try:
        # Check if asked item is exist
        item_to_update = Modules.query.filter(
            Modules.id == id
        ).first()

        if item_to_update is None:
            return json_http_response(
                status=404,
                given_message=_(
                    "Module to update with id=%(id)s is not exist"
                    " in database",
                    id=id
                ),
                dbg=request.args.get('dbg', False)
            )
        else:
            old_item_name = item_to_update.name
        # ----------------------------------------------------------------------

        # Get parameters from request
        version = request.args.get('version', None)
        description = request.args.get('description', None)
        name = request.args.get('name', None)
        # ----------------------------------------------------------------------

        # Check element name (should be a string in 1-50 range)
        if name:
            name = variable_type_check(name.strip(), str)
            if not name.result:
                return json_http_response(
                    status=400,
                    given_message=_(
                        "Value «%(value)s» from parameter"
                        " «&name=%(value)s» is not type of «%(type)s»",
                        value=name.value,
                        type=name.type
                    ),
                    dbg=request.args.get('dbg', False)
                )
            if len(name.value) > 50:
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
                        "Value «%(value)s» from parameter"
                        " «&name=%(value)s» is out of range 1-50",
                        value=answer_string
                    ),
                    dbg=request.args.get('dbg', False)
                )
            elif (len(name.value) > 0) and (
                    name.value != item_to_update.name
            ):
                item_to_update.name = name.value
        # ----------------------------------------------------------------------

        # Check element description (should be a string in 1-256 range)
        if description:
            description = variable_type_check(description.strip(), str)
            if not description.result:
                return json_http_response(
                    status=400,
                    given_message=_(
                        "Value «%(value)s» from parameter"
                        " «&name=%(value)s» is not type of «%(type)s»",
                        value=description.value,
                        type=description.type
                    ),
                    dbg=request.args.get('dbg', False)
                )
            if len(description.value) > 256:
                answer_string = str(
                    description.value[:5]
                )+"..."+str(
                    description.value[-5:]
                ) if len(
                    description.value
                ) > 10 else description.value
                return json_http_response(
                    status=400,
                    given_message=_(
                        "Value «%(value)s» from parameter"
                        " «&name=%(value)s» is out of range 1-50",
                        value=answer_string
                    ),
                    dbg=request.args.get('dbg', False)
                )
            elif (len(description.value) > 0) and (
                    description.value != item_to_update.description
            ):
                item_to_update.description = description.value
        # ----------------------------------------------------------------------

        # Check element description (should be a string in 1-256 range)
        if version:
            version = variable_type_check(version.strip(), str)
            if not version.result:
                return json_http_response(
                    status=400,
                    given_message=_(
                        "Value «%(value)s» from parameter"
                        " «&name=%(value)s» is not type of «%(type)s»",
                        value=description.value,
                        type=description.type
                    ),
                    dbg=request.args.get('dbg', False)
                )
            if len(version.value) > 9:
                answer_string = str(
                    version.value[:5]
                )+"..."+str(
                    version.value[-5:]
                ) if len(
                    version.value
                ) > 10 else version.value
                return json_http_response(
                    status=400,
                    given_message=_(
                        "Value «%(value)s» from parameter"
                        " «&version=%(value)s» is out of range 1-9",
                        value=answer_string
                    ),
                    dbg=request.args.get('dbg', False)
                )
            if not (
                bool(re.match(r"^\d{1,2}.\d{1,2}.\d{1,2}$", version.value))
            ):
                return json_http_response(
                    status=400,
                    given_message=_(
                        "Value «%(value)s» from parameter"
                        " «&version=%(value)s» is not match to"
                        " <major>.<minor>.<patch> (max 2 digit number)",
                        value=version.value,
                    ),
                    dbg=request.args.get('dbg', False)
                )
            elif (len(version.value) > 0) and (
                    version.value != item_to_update.version
            ):
                item_to_update.version = version.value

        # ----------------------------------------------------------------------

        # If session has changes then commit it form output message
        if db.session.dirty:
            db.session.commit()

            schema = ModulesSchema()
            data = schema.dump(item_to_update)

            output_json = {
                "message": _(
                    "Successfully updated element «%(name)s»",
                    name=old_item_name
                ),
                "item": data['links'],
                "responseType": _("Success"),
                "status": 200
            }
        # Else just form output message
        else:

            schema = ModulesSchema()
            data = schema.dump(item_to_update)

            output_json = {
                "message": _(
                    "Item «%(name)s» is stay unchanged by one of the"
                    " reasons: 1. you did not submit data 2. submitted data is"
                    " the same as old 3. element information update is not"
                    " allowed",
                    name=old_item_name
                ),
                "links": data['links'],
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
