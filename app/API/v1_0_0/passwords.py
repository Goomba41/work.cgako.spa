"""Views of API version 1.0.0: System modules and modules types."""

from flask import request, Response, json, current_app as app, url_for, \
    render_template
from flask_babel import _
from flask_mail import Message

from app import db, mail
from datetime import datetime, timedelta
from zxcvbn import zxcvbn
import bcrypt

from .blueprint import APIv1_0_0
from app.models import Users, Passwords
from app.schemas import PasswordsSchema
from .utils import json_http_response, variable_type_check, \
    password_generator, marshmallow_excluding_converter, \
    marshmallow_only_fields_converter, \
    sqlalchemy_filters_converter, sqlalchemy_orders_converter, \
    pagination_of_list


@APIv1_0_0.route('/passwords/', methods=['GET'])
# @token_required
def get_passwords():
    """Get passwords list."""
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
                    Passwords, exclusions_list
                )
                if 'id' in exclusions_list:
                    exclusions_list.remove('id')
                dump_params['exclude'] = exclusions_list
            if columns_list:
                columns_list = marshmallow_only_fields_converter(
                    Passwords, columns_list
                )
                dump_params['only'] = ["id"] + columns_list
        except Exception as error:
            return error.args[0]

        schema = PasswordsSchema(**dump_params)
        # ----------------------------------------------------------------------

        # Make empty base query and if
        # filters and orders exist - add it to query
        elements = Passwords.query

        if filters_list:
            try:
                filters_list = sqlalchemy_filters_converter(
                    Passwords,
                    filters_list
                )
            except Exception as error:
                return error.args[0]
            elements = elements.filter(*filters_list)
        if orders_list:
            try:
                orders_list = sqlalchemy_orders_converter(
                    Passwords, orders_list
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
                '.get_passwords',
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


@APIv1_0_0.route('/passwords/<int:id>', methods=['GET'])
# @token_required
def get_passwords_item(id):
    """Get passwords item by id."""
    try:
        # Get parameters from request
        exclusions_list = request.args.get('exclude')
        columns_list = request.args.get('columns')
        # ----------------------------------------------------------------------

        # Forming dumping parameters
        dump_params = {}

        # Check if values of getted parameters exist in database table
        # and set dump settings
        try:
            if exclusions_list:
                exclusions_list = marshmallow_excluding_converter(
                    Passwords, exclusions_list
                )
                if 'id' in exclusions_list:
                    exclusions_list.remove('id')
                dump_params['exclude'] = exclusions_list
            if columns_list:
                columns_list = marshmallow_only_fields_converter(
                    Passwords, columns_list
                )
                dump_params['only'] = ["id"] + columns_list
        except Exception as error:
            return error.args[0]

        schema = PasswordsSchema(**dump_params)
        # ----------------------------------------------------------------------

        # Query item from database, and if is not none dump it
        item = Passwords.query.get(id)
        if not item:
            return json_http_response(
                status=404,
                given_message=_(
                    "Password with id=%(id)s doesn't exist in database",
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


@APIv1_0_0.route('/passwords/', methods=['POST'])
# @token_required
def post_passwords_item():
    """Post passwords item."""
    try:
        # Get parameters from request
        value = request.args.get('value', None)
        user = request.args.get('user', None)
        # ----------------------------------------------------------------------

        # Check and set user (should be an integer number existed in database)
        if user:
            user = variable_type_check(user, int)
            if not user.result:
                return json_http_response(
                    status=400,
                    given_message=_(
                        "Value «%(value)s» from parameter"
                        " «&user=%(value)s» is not type of «%(type)s»",
                        value=user.value,
                        type=user.type
                    ),
                    dbg=request.args.get('dbg', False)
                )
            user_obj = Users.query.get(user.value)
            if not user_obj:
                return json_http_response(
                    status=404,
                    given_message=_(
                        "Add password to user with id=%(id)s is impossible:"
                        " user is does not exist in database",
                        id=user.value
                    ),
                    dbg=request.args.get('dbg', False)
                )
        else:
            return json_http_response(
                status=400,
                given_message=_(
                    "You don't provide user in parameter"
                    " «&user=», so adding password has been terminated"
                ),
                dbg=request.args.get('dbg', False)
            )
        # ----------------------------------------------------------------------

        # Check and set password value (string
        # in 16-64 range unique in entire database)
        if value:
            value = variable_type_check(value.strip(), str)
            if not value.result:
                return json_http_response(
                    status=400,
                    given_message=_(
                        "Value «%(value)s» from parameter"
                        " «&value=%(value)s» is not type of «%(type)s»",
                        value=value.value,
                        type=value.type
                    ),
                    dbg=request.args.get('dbg', False)
                )
            if len(value.value) > 64 or len(value.value) < 16:
                answer_string = str(
                    value.value[:5]
                )+"..."+str(
                    value.value[-5:]
                ) if len(
                    value.value
                ) > 10 else value.value
                return json_http_response(
                    status=400,
                    given_message=_(
                        "Value «%(value)s» from parameter"
                        " «&value=%(value)s» is out of range 16-64 symbols"
                        " (length is %(l)s)",
                        value=answer_string,
                        l=len(value.value)
                    ),
                    dbg=request.args.get('dbg', False)
                )
            else:
                # If the value exists and passes validation, check it for user
                # data content, strength, and presence in the database for
                # that user.
                pass_test = zxcvbn(value.value, user_inputs=[
                    user_obj.login,
                    user_obj.name,
                    user_obj.surname,
                    user_obj.patronymic,
                    user_obj.phone,
                    user_obj.birth_date,
                    user_obj.employment_date,
                ])

                uinp = pass_test['sequence']

                for element in uinp:
                    if element['pattern'] in 'dictionary' and \
                            element['dictionary_name'] in 'user_inputs':
                        return json_http_response(
                            status=400,
                            given_message=_(
                                "You are using a word from user data (word"
                                " «%(forbidden)s»). You need to change that.",
                                forbidden=element['token']
                            ),
                            dbg=request.args.get('dbg', False)
                        )

                pp = app.config['PASSWORD_POLICY']

                if pp.test(value.value):
                    return json_http_response(
                        status=400,
                        given_message=_(
                            "A password, that was send, is not secure"
                            " Try changing it or"
                            " request a password with the default terms by"
                            " the link (%(link)s).",
                            link=url_for(
                                ".get_passwords_autogenerated",
                                _external=True
                            )
                        ),
                        dbg=request.args.get('dbg', False)
                    )

                up = Passwords.query.filter(
                    Passwords.user_id == user.value
                ).all()
                for p in up:
                    old_hash = (p.salt + p.value).encode('utf8')
                    if bcrypt.checkpw(value.value.encode('utf8'), old_hash):
                        return json_http_response(
                            status=400,
                            given_message=_(
                                "This password was previously used for the"
                                " user «%(login)s». Choose another password.",
                                login=user_obj.login
                            ),
                            dbg=request.args.get('dbg', False)
                        )
                # --------------------------------------------------------------
        else:
            return json_http_response(
                status=400,
                given_message=_(
                    "You don't provide password value in parameter"
                    " «&value=», so adding password has been terminated"
                ),
                dbg=request.args.get('dbg', False)
            )

        # Block old active passwords
        filter = {'user_id': user_obj.id, 'blocked': False}
        active_passwords = Passwords.query.filter_by(**filter).all()
        for password in active_passwords:
            password.blocked = True
        # ----------------------------------------------------------------------

        # Add new password to user
        salt = bcrypt.gensalt()
        password_encrypted = bcrypt.hashpw(
            value.value.encode('utf8'),
            salt
        ).decode('utf-8').replace(salt.decode('utf-8'), '')

        add_password = Passwords(
            user_id=user.value,
            salt=salt.decode('utf-8'),
            value=password_encrypted,
            active_until=datetime.now()+timedelta(
                days=app.config['USER_PASSWORD_RENEW']
            ),
        )
        db.session.add(add_password)
        # db.session.commit()
        # ----------------------------------------------------------------------

        # Send email if password was changed
        html = render_template(
            'change_password.html'
        )
        subject = 'Изменен пароль Вашей учетной записи в ИС'
        ' подразделения ГАСПИ'

        for email in user_obj.emails:
            message = Message(
                subject,
                html=html,
                recipients=[email.value],
                sender=app.config['MAIL_DEFAULT_SENDER']
            )
            try:
                mail.send(message)
            except Exception:
                pass
        # ----------------------------------------------------------------------

        response = json_http_response(
            status=200,
            given_message=_(
                "Successfully added password to user «%(user)s»!",
                user=user_obj.login
            ),
            dbg=request.args.get('dbg', False)
        )

    except Exception:

        response = json_http_response(dbg=request.args.get('dbg', False))

    return response


@APIv1_0_0.route('/passwords/<int:id>', methods=['PUT'])
# @token_required
def put_passwords_item(id):
    """Update passwords item by id."""
    try:

        # Get update target password
        target = Passwords.query.get(id)

        if target is None:
            return json_http_response(
                status=404,
                given_message=_(
                    "Password to update with id=%(id)s is not exist"
                    " in database",
                    id=id
                ),
                dbg=request.args.get('dbg', False)
            )
        # ----------------------------------------------------------------------

        # Get parameters from request
        blocked = request.args.get('blocked', None)

        # Check password blocked status value (should be a boolean)
        if blocked:
            blocked = variable_type_check(blocked, bool)
            if not blocked.result:
                return json_http_response(
                    status=400,
                    given_message=_(
                        "Value «%(value)s» from parameter «&blocked=%(value)s»"
                        " is not type of «%(type)s»",
                        value=blocked.value,
                        type=blocked.type
                    ),
                    dbg=request.args.get('dbg', False)
                )
            # If paramenter passes validation then change database value
            elif blocked.value != target.blocked:
                if not blocked.value:
                    filter = {'user_id': target.user_id, 'blocked': False}
                    user_passwords = Passwords.query.filter_by(**filter).all()
                    for password in user_passwords:
                        if password:
                            password.blocked = True
                else:
                    # Send email if password was blocked
                    html = render_template(
                        'block_password.html'
                    )
                    subject = 'Блокировка учетной записи в ИС'
                    ' подразделения ГАСПИ'
                    user = Users.query.get(target.user_id)
                    for email in user.emails:
                        message = Message(
                            subject,
                            html=html,
                            recipients=[email.value],
                            sender=app.config['MAIL_DEFAULT_SENDER']
                        )

                        try:
                            mail.send(message)
                        except Exception:
                            pass
                target.blocked = blocked.value
                db.session.commit()

                response = json_http_response(
                    status=200,
                    given_message=_(
                        "Password updated!"
                    ),
                    dbg=request.args.get('dbg', False)
                )
            # ------------------------------------------------------------------
            else:
                response = json_http_response(
                    status=200,
                    given_message=_(
                        "Password not updated! You are sending the same data!"
                    ),
                    dbg=request.args.get('dbg', False)
                )

    except Exception:

        response = json_http_response(dbg=request.args.get('dbg', False))

    return response


@APIv1_0_0.route('/passwords/generator', methods=['GET'])
# @token_required
def get_passwords_autogenerated():
    """Get password autogenerated item."""
    try:

        # Get generation parameters from query
        s = variable_type_check(request.args.get('size', 16), int)
        ss = variable_type_check(request.args.get('symbols', True), bool)
        n = variable_type_check(request.args.get('numeric', True), bool)
        al = variable_type_check(request.args.get('alpha_lower', True), bool)
        au = variable_type_check(request.args.get('alpha_upper', True), bool)
        es = variable_type_check(
            request.args.get('exclude_similar', True),
            bool
        )
        ea = variable_type_check(
            request.args.get('exclude_ambiguous', True),
            bool
        )
        # ----------------------------------------------------------------------

        # Validate parameters
        if not s.result:
            return json_http_response(
                status=400,
                given_message=_(
                    "Value «%(value)s» from parameter «&size=%(value)s»"
                    " is not type of «%(type)s»",
                    value=s.value,
                    type=s.type
                ),
                dbg=request.args.get('dbg', False)
            )
        elif len(s.value) > 64 or len(s.value) < 16:
            answer_string = str(
                s.value[:5]
            )+"..."+str(
                s.value[-5:]
            ) if len(
                s.value
            ) > 10 else s.value
            return json_http_response(
                status=400,
                given_message=_(
                    "Value «%(value)s» from parameter"
                    " «&value=%(value)s» is out of range 16-64 symbols"
                    " (length is %(l)s)",
                    value=answer_string,
                    l=len(s.value)
                ),
                dbg=request.args.get('dbg', False)
            )
        if not ss.result:
            return json_http_response(
                status=400,
                given_message=_(
                    "Value «%(value)s» from parameter «&symbols=%(value)s»"
                    " is not type of «%(type)s»",
                    value=ss.value,
                    type=ss.type
                ),
                dbg=request.args.get('dbg', False)
            )
        if not n.result:
            return json_http_response(
                status=400,
                given_message=_(
                    "Value «%(value)s» from parameter «&numeric=%(value)s»"
                    " is not type of «%(type)s»",
                    value=n.value,
                    type=n.type
                ),
                dbg=request.args.get('dbg', False)
            )
        if not al.result:
            return json_http_response(
                status=400,
                given_message=_(
                    "Value «%(value)s» from parameter «&alpha_lower=%(value)s»"
                    " is not type of «%(type)s»",
                    value=al.value,
                    type=al.type
                ),
                dbg=request.args.get('dbg', False)
            )
        if not au.result:
            return json_http_response(
                status=400,
                given_message=_(
                    "Value «%(value)s» from parameter «&alpha_upper=%(value)s»"
                    " is not type of «%(type)s»",
                    value=au.value,
                    type=au.type
                ),
                dbg=request.args.get('dbg', False)
            )
        if not es.result:
            return json_http_response(
                status=400,
                given_message=_(
                    "Value «%(value)s» from parameter «&exclude_similar="
                    "%(value)s» is not type of «%(type)s»",
                    value=es.value,
                    type=es.type
                ),
                dbg=request.args.get('dbg', False)
            )
        if not ea.result:
            return json_http_response(
                status=400,
                given_message=_(
                    "Value «%(value)s» from parameter «&exclude_ambiguous="
                    "%(value)s» is not type of «%(type)s»",
                    value=ea.value,
                    type=ea.type
                ),
                dbg=request.args.get('dbg', False)
            )
        # ----------------------------------------------------------------------

        # Generate initial password with parameters
        password = password_generator(
            size=s.value,
            symbols=ss.value,
            numeric=n.value,
            alpha_lower=al.value,
            alpha_upper=au.value,
            exclude_similar=es.value,
            exclude_ambiguous=ea.value
        )

        # Get the password policy from the config and set the counter of
        # attempts to generate a strong password
        pp = app.config['PASSWORD_POLICY']
        attempts = 0
        # ----------------------------------------------------------------------

        # Generate a new password and count the generation attempt until the
        # password is strong enough
        while pp.test(password) and attempts != 100:
            password = password_generator(
                size=s.value,
                symbols=ss.value,
                numeric=n.value,
                alpha_lower=al.value,
                alpha_upper=au.value,
                exclude_similar=es.value,
                exclude_ambiguous=ea.value
            )
            attempts += 1
        # ----------------------------------------------------------------------

        # If password still not strong enough respond by an error, else respond
        # by generated password
        if pp.test(password):
            return json_http_response(
                status=400,
                given_message=_(
                    "After %(tries)s attempts to generate a password,"
                    " a secure password that meets the specified conditions"
                    " was not received. Try changing the terms or"
                    " request a password with the default terms.",
                    tries=attempts
                ),
                dbg=request.args.get('dbg', False)
            )

        data = {
            "message": _(
                "Generated password is: %(password)s",
                password=password
            ),
            'value': password,
            'responseType': _('Success'),
            'status': 200
        }
        response = Response(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )
        # ----------------------------------------------------------------------
    except Exception:

        response = json_http_response(dbg=request.args.get('dbg', False))

    return response
