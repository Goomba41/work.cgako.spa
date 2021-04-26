"""Views of API version 1.0.0: System modules and modules types."""

# import re

from flask import request, Response, json  # , url_for
# from flask_babel import _
# from app import db

from .blueprint import APIv1_0_0
from app.models import Emails
from app.schemas import EmailsSchema
from .utils import json_http_response
# , marshmallow_excluding_converter, \
#     marshmallow_only_fields_converter, sqlalchemy_filters_converter, \
#     sqlalchemy_orders_converter, pagination_of_list, variable_type_check


@APIv1_0_0.route('/emails/', methods=['GET'])
# @token_required
def get_emails():
    """Get emails list."""
    try:
        # Get parameters from request
        # filters_list = request.args.get('filters')
        # exclusions_list = request.args.get('exclude')
        # columns_list = request.args.get('columns')
        # orders_list = request.args.get('order_by')
        # ----------------------------------------------------------------------

        # Forming dumping parameters
        # dump_params = {'many': True}

        # Check if values of getted parameters exist in database table
        # and set dump settings
        # try:
        #     if exclusions_list:
        #         exclusions_list = marshmallow_excluding_converter(
        #             Modules, exclusions_list
        #         )
        #         if 'id' in exclusions_list:
        #             exclusions_list.remove('id')
        #         dump_params['exclude'] = exclusions_list
        #     if columns_list:
        #         columns_list = marshmallow_only_fields_converter(
        #             Modules, columns_list
        #         )
        #         dump_params['only'] = ["id"] + columns_list
        # except Exception as error:
        #     return error.args[0]
        #
        # schema = ModulesSchema(**dump_params)
        # ----------------------------------------------------------------------

        # Make empty base query and if
        # filters and orders exist - add it to query
        # elements = Modules.query

        # if filters_list:
        #     try:
        #         filters_list = sqlalchemy_filters_converter(
        #             Modules,
        #             filters_list
        #         )
        #     except Exception as error:
        #         return error.args[0]
        #     elements = elements.filter(*filters_list)
        # if orders_list:
        #     try:
        #         orders_list = sqlalchemy_orders_converter(
        #             Modules, orders_list
        #         )
        #     except Exception as error:
        #         return error.args[0]
        #     elements = elements.order_by(*orders_list)
        # ----------------------------------------------------------------------

        # data = schema.dump(elements.all())

        # Paginating results of dumping
        # Probably would best is pagination in sqlalchemy query?
        # data = pagination_of_list(
        #     data,
        #     url_for(
        #         '.get_modules',
        #         _external=True
        #     ),
        #     query_params=request.args
        # )
        # ----------------------------------------------------------------------

        response = Response(
            response=json.dumps("OK"),
            status=200,
            mimetype='application/json'
        )
    except Exception:

        response = json_http_response(dbg=request.args.get('dbg', False))

    return response


@APIv1_0_0.route('/emails/<int:id>', methods=['GET'])
# @token_required
def get_emails_item(id):
    """Get emails item by id."""
    try:
        print(f"GET EMAIL {id}")
        response = json_http_response(
            status=200,
            dbg=request.args.get('dbg', False)
        )
    except Exception:

        response = json_http_response(dbg=request.args.get('dbg', False))

    return response


@APIv1_0_0.route('/emails/', methods=['POST'])
# @token_required
def post_emails_item():
    """Post emails item by id."""
    try:
        print("POST EMAIL")
        response = json_http_response(
            status=200,
            dbg=request.args.get('dbg', False)
        )
    except Exception:

        response = json_http_response(dbg=request.args.get('dbg', False))

    return response


@APIv1_0_0.route('/emails/<int:id>', methods=['DELETE'])
# @token_required
def delete_emails_item(id):
    """Delete emails item by id."""
    try:
        print(f"DELETE EMAIL {id}")
        response = json_http_response(
            status=200,
            dbg=request.args.get('dbg', False)
        )
    except Exception:

        response = json_http_response(dbg=request.args.get('dbg', False))

    return response


@APIv1_0_0.route('/emails/<int:id>', methods=['PUT'])
# @token_required
def put_emails_item(id):
    """Update emails item by id."""
    try:
        print(f"UPDATE EMAIL {id}")
        response = json_http_response(
            status=200,
            dbg=request.args.get('dbg', False)
        )
    except Exception:

        response = json_http_response(dbg=request.args.get('dbg', False))

    return response
