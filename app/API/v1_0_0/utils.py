"""Additional utilities, used without route."""

from random import SystemRandom
from flask import Response, json, request, current_app as app
from flask_babel import _
from distutils.util import strtobool
from urllib.parse import urljoin
from sqlalchemy.inspection import inspect
from collections import namedtuple
# from functools import wraps

import math
import traceback
import sys


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
        response_type = _('Error')
        if status == 400:
            message = _('Bad request!')
        if status == 401:
            message = _('Unauthorized!')
        if status == 403:
            message = _('Forbidden')
        if status == 404:
            message = _('Not found!')
        if status == 500:
            message = _('Internal server error!')
    elif status in (200, 201):
        response_type = _('Success')
        if status == 200:
            message = 'OK!'
        if status == 201:
            message = _('Created!')
    elif status in (304,):
        response_type = _('Warning')
        message = _('Not modified!')
    else:
        response_type = _('Info')
        message = _('I don`t know what to say! Probably this'
                    'is test response?')

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
            if sys.exc_info()[2]:
                info['debugInfo'] = traceback.format_exc()
    else:
        try:
            if strtobool(dbg):
                if sys.exc_info()[2]:
                    info['debugInfo'] = traceback.format_exc()
        except Exception:
            info['debugInfo'] = _(
                "Debugging info is turned off, because "
                "incorrect type of parameter 'dbg' (should be boolean)"
            )

    return Response(
        response=json.dumps(info),
        status=status,
        mimetype='application/json'
    )


def class_attribute_existence(exclude_model, exclude_fields):
    """Deep check for the existence of a class attribute."""
    exclude_fields = [
        x.strip() for x in
        exclude_fields.split(".")
    ]
    if len(exclude_fields) == 1:
        if hasattr(exclude_model, exclude_fields[0]):
            return True
        else:
            return False
    else:
        for item in exclude_fields:
            i = inspect(exclude_model).relationships
            referred_classes = [r.mapper.class_ for r in i]
            for cls in referred_classes:
                if cls.__tablename__ and cls.__tablename__ == item:
                    return class_attribute_existence(
                        cls, '.'.join(exclude_fields[1:])
                    )
                elif cls.__tablename__ != item and len(exclude_fields) > 1:
                    continue
                elif not hasattr(
                    exclude_model,
                    item
                ) and len(exclude_fields) == 1:
                    return False
                else:
                    return True
    return False


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
        try:
            filter_parameters = [
                x.strip() for x in
                filter_parameters.split(",")
            ]
        except Exception:
            raise Exception(json_http_response(
                status=400,
                given_message=_(
                    "Parsing error of list of filters «%(filters)s» from"
                    " parameter «&filter=%(filters)s». Be sure that fields"
                    " separated by comma.",
                    filters=filter_parameters
                ),
                dbg=request.args.get('dbg', False)
            ))
        for parameter in filter_parameters:
            try:
                column_name, op, value = [
                    x.strip() for x in
                    parameter.split(':')
                ]
            except Exception:
                # Raise exception with response object as parameter
                # for reraising it in parent function
                raise Exception(json_http_response(
                    status=400,
                    given_message=_(
                        "Invalid filter «%(filter)s» (should be"
                        " «filter=<column>:<operator>:<value>»)",
                        filter=parameter
                    ),
                    dbg=request.args.get('dbg', False)
                ))
            if op not in dict_filtros_op:
                variants = ', '.join(list(dict_filtros_op.keys()))
                raise Exception(json_http_response(
                    status=400,
                    given_message=_(
                        "Invalid filter operator «%(operator)s» (possible"
                        " variants is: %(variants)s",
                        operator=parameter,
                        variants=variants
                    ),
                    dbg=request.args.get('dbg', False)
                ))

            # Verifying that model has a column, else NONE
            column = getattr(model, column_name, None)

            if not column:
                raise Exception(json_http_response(
                    status=400,
                    given_message=_(
                        "Column «%(column)s» from filter «%(filter)s»"
                        " doesn't exist in model «%(model)s»",
                        column=column_name,
                        filter=parameter,
                        model=model.__name__
                    ),
                    dbg=request.args.get('dbg', False)
                ))
            # If operator is 'in', then parse value string to get values
            if dict_filtros_op[op] == 'in':
                try:
                    value = [x.strip() for x in value.split(",")]
                    filters_list.append(column.in_(value))
                except Exception:
                    raise Exception(json_http_response(
                        status=400,
                        given_message=_(
                            "Error of translating value «%(value)s» to"
                            " list of values (in case of «in» operator <value>"
                            " must be string of values, delimited by «,»)",
                            value=value
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
                    if dict_filtros_op[op] == 'like':
                        value = f"%{value}%"
                    filters_list.append(getattr(column, attr)(value))
                except Exception:
                    raise Exception(json_http_response(
                        status=400,
                        given_message=_(
                            "Error of translating filter operator «%(op)s»",
                            op=parameter
                        ),
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
        try:
            order_parameters = [x.strip() for x in order_parameters.split(",")]
        except Exception:
            raise Exception(json_http_response(
                status=400,
                given_message=_(
                    "Parsing error of list of orderings «%(value)s» from"
                    " parameter «&order_by=%(value)s». Be sure that fields"
                    " separated by comma.",
                    value=order_parameters
                ),
                dbg=request.args.get('dbg', False)
            ))
        for order in order_parameters:

            try:
                column_name, direction = [x.strip() for x in order.split(':')]
            except Exception:
                # Raise exception with response object as parameter
                # for reraising it in parent function
                raise Exception(json_http_response(
                    status=400,
                    given_message=_(
                        "Invalid order parameter «%(value)s» (should be"
                        "«order_by=<column>:<direction>»)",
                        value=order
                    ),
                    dbg=request.args.get('dbg', False)
                ))
            if direction.lower() not in ["asc", "desc"]:
                raise Exception(json_http_response(
                    status=400,
                    given_message=_(
                        "Invalid order direction «%(direction)s» in order"
                        " parameter «%(order)s» (possible"
                        " variants is: «acs», «desc»)",
                        direction=direction,
                        order=order
                    ),
                    dbg=request.args.get('dbg', False)
                ))

            column = getattr(model, column_name, None)

            if not column:
                raise Exception(json_http_response(
                    status=400,
                    given_message=_(
                        "Column «%(column)s» from order parameter «%(order)s»"
                        " doesn't exist in model «%(model)s»",
                        column=column_name,
                        order=order,
                        model=model.__name__
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
                    given_message=_(
                        "Error of translating order by"
                        " operator «%(operator)s»",
                        operator=order
                    ),
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
    try:
        only_fields_parameters = [
            x.strip() for x in
            only_fields_parameters.split(",")
        ]
    except Exception:
        raise Exception(json_http_response(
            status=400,
            given_message=_(
                "Parsing error of list of columns «%(only)s» from"
                " parameter «&columns=%(only)s». Be sure that fields separated"
                " by comma.",
                only=only_fields_parameters
            ),
            dbg=request.args.get('dbg', False)
        ))
    for column in only_fields_parameters:
        if not class_attribute_existence(model, column):
            raise Exception(json_http_response(
                status=400,
                given_message=_(
                    "Column «%(items)s» from column parameter "
                    "«&column=%(columns)s» doesn't exist in model «%(model)s»",
                    items=column.split(".")[-1],
                    columns=column,
                    model=model.__name__
                ),
                dbg=request.args.get('dbg', False)
            ))

    # Remove fields not present in the model from the list
    only_fields_parameters[:] = [
        x for x in only_fields_parameters if class_attribute_existence(
            model, x
        )
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
    try:
        exclusions_parameters = [
            x.strip() for x in
            exclusions_parameters.split(",")
        ]
    except Exception:
        raise Exception(json_http_response(
            status=400,
            given_message=_(
                "Parsing error of list of exclusions «%(items)s» from "
                "parameter «&exclude=%(items)s». Be sure that fields separated"
                " by comma.",
                items=exclusions_parameters
            ),
            dbg=request.args.get('dbg', False)
        ))
    for exclude in exclusions_parameters:
        if not class_attribute_existence(model, exclude):
            raise Exception(json_http_response(
                status=400,
                given_message=_(
                    "Column «%(column)s» from exclude parameter "
                    "«&exclude=%(items)s» doesn't exist in model «%(model)s»",
                    column=exclude.split(".")[-1],
                    items=exclude,
                    model=model.__name__
                ),
                dbg=request.args.get('dbg', False)
            ))

    # Remove fields not present in the model from the list
    exclusions_parameters[:] = [
        x for x in exclusions_parameters if class_attribute_existence(model, x)
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
            limit = app.config['LIMIT']
    elif limit < 1:
        limit = app.config['LIMIT']

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


def variable_type_check(value, type):
    """Variable type check and convert."""
    TypeCheck = namedtuple(
        typename="TypeCheck",
        field_names=["result", "type", "value"]
    )
    if type is bool:
        if not isinstance(value, type):
            try:
                value = strtobool(value)
                return TypeCheck(True, type.__name__, value)
            except Exception:
                return TypeCheck(False, type.__name__, value)
        else:
            return TypeCheck(True, type.__name__, value)
    if type is int:
        if not isinstance(value, type):
            try:
                value = int(value)
                return TypeCheck(True, type.__name__, value)
            except Exception:
                return TypeCheck(False, type.__name__, value)
        else:
            return TypeCheck(True, type.__name__, value)
    if type is str:
        if not isinstance(value, type):
            try:
                value = str(value)
                return TypeCheck(True, type.__name__, value)
            except Exception:
                return TypeCheck(False, type.__name__, value)
        else:
            return TypeCheck(True, type.__name__, value)
    return TypeCheck(False, type.__name__, value)

# Example of decorator

# def language_detect(function):
#     """Language detection for i18n decorator."""
#     @wraps(function)
#     def wrapper(*args, **kwargs):
#         print("language detection before function call")
#         print(request.host)
#         return function(*args, **kwargs)
#     return wrapper
