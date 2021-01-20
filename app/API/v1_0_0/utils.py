"""Additional utilities, used without route."""

from random import SystemRandom
from flask import Response, json, request, current_app as app
from distutils.util import strtobool
from urllib.parse import urljoin

import math
import traceback


def password_generator(size=8):
    """Password generation with a given length."""
    # Defining alphabets for different characher types
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    alphabet_upper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    numeric = '0123456789'
    special = '!@#$%^&*()_+~`|}{[]:;?><,./-='
    cryptogen = SystemRandom()

    # Joining alphabets in set
    character_set = alphabet + alphabet_upper + numeric + special

    # Get 4 random character from set for password
    password_symbols = ''.join(
        cryptogen.choice(character_set) for i in range(size - 4)
    )

    # Get one character from each type,
    # lowercase and uppercase latin, number, special symbol
    password_symbols += cryptogen.choice(alphabet)
    password_symbols += cryptogen.choice(alphabet_upper)
    password_symbols += cryptogen.choice(numeric)
    password_symbols += cryptogen.choice(special)

    # Converting taken symbols of password from string to list
    password_symbols = list(map(str, password_symbols))

    # Mixing symbols in list with Fisher-Yates algorithm
    for i in range(len(password_symbols) - 1, 0, -1):
        j = math.floor(cryptogen.random() * (i + 1))
        temp = password_symbols[j]
        password_symbols[j] = password_symbols[i]
        password_symbols[i] = temp

    # Converting back to string and return
    password_symbols = ''.join(password_symbols)

    return password_symbols


def json_http_response(dbg=False, given_message=None, status=500):
    """
    Server response generation.

    Supported parameters:
    dbg (Boolean) - add additional info in traceback format (False by default)
    given_message (String) - set reponse message manually (None by default)
    status (Integer) - set response status manually (500 by default)
    """
    # Defining message and response type depending on status
    if status in (400, 401, 403, 404, 500):
        response_type = 'Error'
        if status == 400:
            message = 'Bad request!'
        if status == 401:
            message = 'Unauthorized!'
        if status == 403:
            message = 'Forbidden'
        if status == 404:
            message = 'Not found!'
        if status == 500:
            message = 'Internal server error!'
    elif status in (200, 201):
        response_type = 'Success'
        if status == 200:
            message = 'OK!'
        if status == 201:
            message = 'Created!'
    elif status in (304,):
        response_type = 'Warning'
        message = 'Not modified!'
    else:
        response_type = 'Info'
        message = 'I don`t know what to say! Probably this is test response?'

    info = {
        'responseType': response_type,
        'message': message,
        'status': status
    }

    info['message'] = given_message if given_message is not None else message

    # Try to convert dbg parameter to boolean and if True,
    # add debug information to response
    if isinstance(dbg, bool):
        if dbg is True:
            info['debugInfo'] = traceback.format_exc()
    else:
        try:
            if strtobool(dbg):
                info['debugInfo'] = traceback.format_exc()
        except Exception:
            info['debugInfo'] = "Debugging info is turned off, because "
            "incorrect type of value of parameter 'dbg' (should be boolean)"

    return Response(
        response=json.dumps(info),
        status=status,
        mimetype='application/json'
    )


# This function does not currently implement the
# 'and' and 'or' operators for the filter. Maybe in future?
def sqlalchemy_filters_converter(model, filter_parameters=[]):
    """
    Filter converter to sqlaclhemy format.

    Supported parameters:
    model (Model) - Model for which translate filters
    filter_parameters (List) - List of filters obtained from the request
    """
    dict_filtros_op = {
        '==': 'eq',
        '!=': 'ne',
        '>': 'gt',
        '<': 'lt',
        '>=': 'ge',
        '<=': 'le',
        'like': 'like',
        'ilike': 'ilike',
        'in': 'in'
    }

    filters_list = []
    if filter_parameters:
        for parameter in filter_parameters:
            try:
                column_name, op, value = parameter.split(':')
            except Exception:
                # Raise exception with response object as parameter
                # for reraising it in parent function
                raise Exception(json_http_response(
                    status=400,
                    given_message="Invalid filter «%s» (should be "
                    "«filter=<column>:<operator>:<value>»)" % (parameter),
                    dbg=request.args.get('dbg', False)
                ))
            if op not in dict_filtros_op:
                raise Exception(json_http_response(
                    status=400,
                    given_message="Invalid filter operator «%s» (possible"
                    " variants is: %s)" % (
                        op,
                        ', '.join(list(dict_filtros_op.keys()))
                    ),
                    dbg=request.args.get('dbg', False)
                ))

            # Verifying that model has a column, else NONE
            column = getattr(model, column_name, None)

            if not column:
                raise Exception(json_http_response(
                    status=400,
                    given_message="Column «%s» from filter «%s» "
                    "doesn't exist in model «%s»" % (
                        column_name,
                        parameter,
                        model.__name__
                    ),
                    dbg=request.args.get('dbg', False)
                ))
            # If operator is 'in', then parse value string to get values
            if dict_filtros_op[op] == 'in':
                try:
                    value = value.split(",")
                    filters_list.append(column.in_(value))
                except Exception:
                    raise Exception(json_http_response(
                        status=400,
                        given_message="Error of translating value «%s» to"
                        " list of values (in case of «in» operator <value>"
                        " must be string of values, delimited by «,»)" % (
                            value
                        ),
                        dbg=request.args.get('dbg', False)
                    ))
            # else forming filter and append it to list of filters
            else:
                try:
                    attr = list(filter(
                        lambda e: hasattr(column, e % dict_filtros_op[op]),
                        ['%s', '%s_', '__%s__']
                    ))[0] % dict_filtros_op[op]
                    filters_list.append(getattr(column, attr)(value))
                except Exception:
                    raise Exception(json_http_response(
                        status=400,
                        given_message="Error of translating filter"
                        " operator «%s»" % (parameter),
                        dbg=request.args.get('dbg', False)
                    ))
    return filters_list


def sqlalchemy_orders_converter(model, order_parameters=[]):
    """
    Order by converter to sqlaclhemy format.

    Supported parameters:s
    model (Model) - Model for which translate filters
    order_parameters (List) - List of orderings obtained from the request
    """
    orders_list = []
    if order_parameters:
        for order in order_parameters:
            try:
                column_name, direction = order.split(':')
            except Exception:
                # Raise exception with response object as parameter
                # for reraising it in parent function
                raise Exception(json_http_response(
                    status=400,
                    given_message="Invalid order parameter «%s» (should be "
                    "«order_by=<column>:<direction>»)" % (order),
                    dbg=request.args.get('dbg', False)
                ))
            if direction.lower() not in ["asc", "desc"]:
                raise Exception(json_http_response(
                    status=400,
                    given_message="Invalid order direction «%s» in order"
                    " parameter «%s» (possible"
                    " variants is: «acs», «desc»)" % (direction, order),
                    dbg=request.args.get('dbg', False)
                ))

            column = getattr(model, column_name, None)

            if not column:
                raise Exception(json_http_response(
                    status=400,
                    given_message="Column «%s» from order parameter «%s» "
                    "doesn't exist in model «%s» " % (
                        column_name,
                        order,
                        model.__name__
                    ),
                    dbg=request.args.get('dbg', False)
                ))

            try:
                attr = list(filter(
                    lambda e: hasattr(column, e % direction),
                    ['%s', '%s_', '__%s__']
                ))[0] % direction
                orders_list.append(getattr(column, attr)())
            except Exception:
                raise Exception(json_http_response(
                    status=400,
                    given_message="Error of translating order by"
                    " operator «%s»" % (order),
                    dbg=request.args.get('dbg', False)
                ))

    return orders_list


def marshmallow_only_fields_converter(model, only_fields_parameters=[]):
    """
    Only fields list converter to sqlaclhemy format.

    Supported parameters:s
    model (Model) - Model for which translate filters
    only_fields_parameters (List) - List of params obtained from the request
    """
    for column in only_fields_parameters:
        if not hasattr(model, column):
            raise Exception(json_http_response(
                status=400,
                given_message="Column «%s» from column parameter "
                "«&column=%s» doesn't exist in model «%s»" % (
                    column,
                    column,
                    model.__name__
                ),
                dbg=request.args.get('dbg', False)
            ))

    # Remove fields not present in the model from the list
    only_fields_parameters[:] = [
        x for x in only_fields_parameters if hasattr(model, x)
    ]

    return only_fields_parameters


def marshmallow_excluding_converter(model, exclusions_parameters=[]):
    """
    Exclusion list checker for field existence in the model.

    Supported parameters:s
    model (Model) - Model for which translate filters
    columns (String) - List of columns to order by (None by default)
    exclusions_parameters (List) - List of exclusions obtained from the request
    """
    for exclude in exclusions_parameters:
        if not hasattr(model, exclude):
            raise Exception(json_http_response(
                status=400,
                given_message="Column «%s» from exclude parameter "
                "«&exclude=%s» doesn't exist in model «%s»" % (
                    exclude,
                    exclude,
                    model.__name__
                ),
                dbg=request.args.get('dbg', False)
            ))

    # Remove fields not present in the model from the list
    exclusions_parameters[:] = [
        x for x in exclusions_parameters if hasattr(model, x)
    ]

    return exclusions_parameters


def pagination_of_list(query_result, url, query_params):
    """
    Pagination of query results.

    Required parameters:
    query_result - result of query in json dictionary
    url - URL API for links generation
    query_params - parameters, sended with query
    """
    start = query_params.get('start', 1)
    limit = query_params.get('limit', app.config['LIMIT'])

    query_params_string = ''

    for i in query_params:
        if i not in ('start', 'limit'):
            query_params_string += '&%s=%s' % (
                i, query_params.get(i).replace(' ', '+')
            )

    records_count = len(query_result)

    if not isinstance(start, int):
        try:
            start = int(start)
        except ValueError:
            start = 1
    elif start < 1:
        start = 1

    if not isinstance(limit, int):
        try:
            limit = int(limit)
        except ValueError:
            limit = 10
    elif limit < 1:
        limit = 10

    if records_count < start and records_count != 0:
        start = records_count
    elif records_count < start and records_count <= 0:
        start = 1

    response_obj = {}
    response_obj['start'] = start
    response_obj['limit'] = limit
    response_obj['itemsCount'] = records_count
    response_obj['currentPage'] = math.floor((start - 1) / limit) + 1

    pages_count = math.ceil(records_count / limit)
    response_obj['pages'] = pages_count if pages_count > 0 else 1

    # Creating URL to previous page
    if start == 1:
        response_obj['previousPage'] = ''
    else:
        start_copy = max(1, start - limit)
        limit_copy = start - 1
        params = '?start=%d&limit=%d%s' % (
            start_copy,
            limit_copy,
            query_params_string
        )
        new_url = urljoin(url,
                          params)
        response_obj['previousPage'] = new_url

    # Creating URL to next page
    if start + limit > records_count:
        response_obj['nextPage'] = ''
    else:
        start_copy = start + limit
        params = '?start=%d&limit=%d%s' % (
            start_copy,
            limit,
            query_params_string
        )
        new_url = urljoin(url,
                          params)
        response_obj['nextPage'] = new_url

    # Query results cutting to limit
    response_obj['pageData'] = query_result[(start - 1):(start - 1 + limit)]

    return response_obj
