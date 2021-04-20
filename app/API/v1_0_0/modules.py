"""Views of API version 1.0.0: User profile."""

from flask import request, Response, json
# , url_for
# from flask_babel import _

from .blueprint import APIv1_0_0
# from app import db
from app.models import ModulesTypes, Modules
from app.schemas import ModulesTypesSchema, ModulesSchema
from .utils import json_http_response
# , marshmallow_excluding_converter, \
#     marshmallow_only_fields_converter, sqlalchemy_filters_converter, \
#     sqlalchemy_orders_converter, pagination_of_list, variable_type_check


@APIv1_0_0.route('/modules/', methods=['GET'])
# @token_required
def get_modules():
    """Get modules list."""
    try:
        print("GET MODULES")
        schema = ModulesSchema(many=True)
        print(schema)

        elements = Modules.query.all()
        data = schema.dump(elements)
        print(data)
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


@APIv1_0_0.route('/modules/types/', methods=['GET'])
# @token_required
def get_modules_types():
    """Get modules types list."""
    try:
        print("GET MODULES TYPES")
        schema = ModulesTypesSchema(many=True)
        print(schema)

        elements = ModulesTypes.query.all()
        data = schema.dump(elements)
        print(data)
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
        print(f"GET MODULE TYPE {id}")
        response = json_http_response(
            status=200,
            dbg=request.args.get('dbg', False)
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
