"""Views of API version 1.0.0: System modules and modules types."""

from flask import request, Response, json, url_for, render_template, \
    current_app as app
from flask_babel import _
from flask_mail import Message
from validate_email import validate_email
from app import db, mail
from datetime import datetime, timedelta

from .blueprint import APIv1_0_0
from app.models import Emails, Users
from app.schemas import EmailsSchema
from .utils import json_http_response, marshmallow_excluding_converter, \
     marshmallow_only_fields_converter, sqlalchemy_filters_converter, \
     sqlalchemy_orders_converter, pagination_of_list, display_time, \
     generate_confirmation_token, confirm_email_token, variable_type_check


@APIv1_0_0.route('/emails/', methods=['GET'])
# @token_required
def get_emails():
    """Get emails list."""
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
                    Emails, exclusions_list
                )
                if 'id' in exclusions_list:
                    exclusions_list.remove('id')
                dump_params['exclude'] = exclusions_list
            if columns_list:
                columns_list = marshmallow_only_fields_converter(
                    Emails, columns_list
                )
                dump_params['only'] = ["id"] + columns_list
        except Exception as error:
            return error.args[0]
        #
        schema = EmailsSchema(**dump_params)
        # ----------------------------------------------------------------------

        # Make empty base query and if
        # filters and orders exist - add it to query
        elements = Emails.query

        if filters_list:
            try:
                filters_list = sqlalchemy_filters_converter(
                    Emails,
                    filters_list
                )
            except Exception as error:
                return error.args[0]
            elements = elements.filter(*filters_list)
        if orders_list:
            try:
                orders_list = sqlalchemy_orders_converter(
                    Emails, orders_list
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


@APIv1_0_0.route('/emails/<int:id>', methods=['GET'])
# @token_required
def get_emails_item(id):
    """Get emails item by id."""
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
                    Emails, exclusions_list
                )
                if 'id' in exclusions_list:
                    exclusions_list.remove('id')
                dump_params['exclude'] = exclusions_list
            if columns_list:
                columns_list = marshmallow_only_fields_converter(
                    Emails, columns_list
                )
                dump_params['only'] = ["id"] + columns_list
        except Exception as error:
            return error.args[0]

        schema = EmailsSchema(**dump_params)
        # ----------------------------------------------------------------------

        # Query item from database, and if is not none dump it
        item = Emails.query.get(id)
        if not item:
            return json_http_response(
                status=404,
                given_message=_(
                    "Email with id=%(id)s doesn't exist in database",
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


@APIv1_0_0.route('/emails/', methods=['POST'])
# @token_required
def post_emails_item():
    """Post emails item by id."""
    try:
        # Get parameters from request
        value = request.args.get('value', None)
        type = request.args.get('type', None)
        user = request.args.get('user', None)

        # Check user (should be an integer number existed in database)
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
                        "Add email to user with id=%(id)s is impossible:"
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
                    " «&user=», so adding email has been terminated"
                ),
                dbg=request.args.get('dbg', False)
            )

        # Check email value (should be a email formated string in 1-100 range
        # unique in entire database)
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
            if len(value.value) > 100:
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
                        " «&value=%(value)s» is out of range 1-100",
                        value=answer_string
                    ),
                    dbg=request.args.get('dbg', False)
                )
            if not validate_email(value.value):
                return json_http_response(
                    status=400,
                    given_message=_(
                        "Something's wrong with email «%(value)s»"
                        " validation: email incorrect or does not exist",
                        value=value.value
                    ),
                    dbg=request.args.get('dbg', False)
                )
            if Emails.query.filter(Emails.value == value.value).first():
                return json_http_response(
                    status=400,
                    given_message=_(
                        "Email «%(value)s» already exist in database: email"
                        " must be unique in entire database",
                        value=value.value
                    ),
                    dbg=request.args.get('dbg', False)
                )
        else:
            return json_http_response(
                status=400,
                given_message=_(
                    "You don't provide email value in parameter"
                    " «&value=», so adding email has been terminated"
                ),
                dbg=request.args.get('dbg', False)
            )

        # Check email type (should be a string in 1-20 range)
        if type:
            type = variable_type_check(type.strip(), str)
            if not type.result:
                return json_http_response(
                    status=400,
                    given_message=_(
                        "Value «%(value)s» from parameter"
                        " «&type=%(value)s» is not type of «%(type)s»",
                        value=type.value,
                        type=type.type
                    ),
                    dbg=request.args.get('dbg', False)
                )
            if len(type.value) > 20:
                answer_string = str(
                    type.value[:5]
                )+"..."+str(
                    type.value[-5:]
                ) if len(
                    type.value
                ) > 10 else type.value
                return json_http_response(
                    status=400,
                    given_message=_(
                        "Value «%(value)s» from parameter"
                        " «&type=%(value)s» is out of range 1-20",
                        value=answer_string
                    ),
                    dbg=request.args.get('dbg', False)
                )

        email = Emails(
            user_id=user.value,
            type=type.value,
            value=value.value,
            verify=0,
            active_until=None,
        )
        db.session.add(email)
        db.session.flush()

        # Before send response, dump newly added email to json and add
        # his data to response
        email_schema = EmailsSchema(
            only=["id", "value", "links", "type"]
        )
        email_dump = email_schema.dump(email)
        db.session.commit()

        output_json = {
            "message": _(
                "Successfully added email «%(email)s»"
                " to user «%(user)s»! Please, check email box for verification"
                " mail.",
                email=value.value,
                user=user_obj.login
            ),
            "email": email_dump,
            "responseType": _("Success"),
            "status": 200
        }
        # ----------------------------------------------------------------------

        response = Response(
            response=json.dumps(output_json),
            status=200,
            mimetype='application/json'
        )

        post_emails_verify_item(email.id)

    except Exception:

        response = json_http_response(dbg=request.args.get('dbg', False))

    return response


@APIv1_0_0.route('/emails/<int:id>', methods=['DELETE'])
# @token_required
def delete_emails_item(id):
    """Delete emails item by id."""
    try:
        item_to_delete = Emails.query.filter(
            Emails.id == id
        ).first()

        if item_to_delete is None:
            return json_http_response(
                status=404,
                given_message=_(
                    "Email to delete with id=%(value)s"
                    " is not exist in database",
                    value=id
                ),
                dbg=request.args.get('dbg', False)
            )

        db.session.delete(item_to_delete)
        db.session.commit()

        return json_http_response(
            status=200,
            given_message=_(
                "Email «%(value)s» successfully deleted from"
                " database",
                value=item_to_delete.value
            ),
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

        message_addition = ''

        # Get update target email
        target = Emails.query.filter(
            Emails.id == id
        ).first()

        if target is None:
            return json_http_response(
                status=404,
                given_message=_(
                    "Email to update with id=%(id)s is not exist"
                    " in database",
                    id=id
                ),
                dbg=request.args.get('dbg', False)
            )
        else:
            target_ov = target.value

        # Get parameters from request
        value = request.args.get('value')
        type = request.args.get('type')

        # Check email value (should be a email formated string in 1-100 range)
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
            if len(value.value) > 100:
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
                        " «&value=%(value)s» is out of range 1-100",
                        value=answer_string
                    ),
                    dbg=request.args.get('dbg', False)
                )
            elif (len(value.value) > 0) and (
                    value.value != target.value
            ):
                if not validate_email(value.value):
                    return json_http_response(
                        status=400,
                        given_message=_(
                            "Something's wrong with email «%(value)s»"
                            " validation: email incorrect or does not exist",
                            value=value.value
                        ),
                        dbg=request.args.get('dbg', False)
                    )
                else:
                    target.value = value.value
                    target.verify = 0
                    target.active_until = None

                    message_addition = _(
                        " Check updated email for"
                        " confirmation mail!"
                    )
        # ----------------------------------------------------------------------

        # Check email type (should be a string in 1-20 range)
        if type:
            type = variable_type_check(type.strip(), str)
            if not type.result:
                return json_http_response(
                    status=400,
                    given_message=_(
                        "Value «%(value)s» from parameter"
                        " «&type=%(value)s» is not type of «%(type)s»",
                        value=type.value,
                        type=type.type
                    ),
                    dbg=request.args.get('dbg', False)
                )
            if len(type.value) > 20:
                answer_string = str(
                    type.value[:5]
                )+"..."+str(
                    type.value[-5:]
                ) if len(
                    type.value
                ) > 10 else type.value
                return json_http_response(
                    status=400,
                    given_message=_(
                        "Value «%(value)s» from parameter"
                        " «&type=%(value)s» is out of range 1-20",
                        value=answer_string
                    ),
                    dbg=request.args.get('dbg', False)
                )
            elif (len(type.value) > 0) and (
                    type.value != target.type
            ):
                target.type = type.value
        # ----------------------------------------------------------------------

        db.session.commit()

        post_emails_verify_item(id)

        response = json_http_response(
            status=200,
            given_message=_(
                "Email «%(value)s» has been updated!",
                value=target_ov
            )+message_addition,
            dbg=request.args.get('dbg', False)
        )
    except Exception:

        response = json_http_response(dbg=request.args.get('dbg', False))

    return response


@APIv1_0_0.route('/emails/verification/<int:id>', methods=['POST'])
# @token_required
def post_emails_verify_item(id):
    """Post emails verify item by id."""
    try:
        recipient = Emails.query.filter(
            Emails.id == id
        ).first()

        if recipient:
            if recipient.active_until:
                begin_verification_period = recipient.active_until-timedelta(
                    days=app.config['USER_MAIL_RENEW_NOTIFICATION']
                )
            else:
                begin_verification_period = datetime.now()+timedelta(
                    hours=1
                )

        if recipient is None:
            return json_http_response(
                status=404,
                given_message=_(
                    "Recipient email with id=%(value)s"
                    " is does not exist in database",
                    value=id
                ),
                dbg=request.args.get('dbg', False)
            )
        elif recipient.verify and datetime.now() < begin_verification_period:
            return json_http_response(
                status=400,
                given_message=_(
                    "Recipient email with id=%(value)s"
                    " already verified. Request ignored",
                    value=id
                ),
                dbg=request.args.get('dbg', False)
            )

        expiration = 3600

        token = generate_confirmation_token(id, expiration)
        confirm_url = app.config['CLIENT_LINK'] + '/email/verify/' + \
            token.decode("utf-8")

        html = render_template(
            'confirmation_mail.html',
            confirm_url=confirm_url,
            active_time="".join(display_time(expiration))
        )
        subject = 'Подтверждение адреса электронной почты в ИС'
        ' подразделения ГАСПИ'

        message = Message(
            subject,
            html=html,
            recipients=[recipient.value],
            sender=app.config['MAIL_DEFAULT_SENDER']
        )

        try:
            mail.send(message)
            response = json_http_response(
                given_message=_(
                    "Mail successfully send to recipient for verification"
                ),
                status=200,
                dbg=request.args.get('dbg', False)
            )
        except Exception:
            response = json_http_response(
                given_message=_(
                    "Something went wrong! Mail prepared, but not sent!"
                ),
                status=400,
                dbg=request.args.get('dbg', False)
            )
    except Exception:

        response = json_http_response(dbg=request.args.get('dbg', False))

    return response


@APIv1_0_0.route('/emails/verification/<string:vstring>', methods=['PUT'])
# @token_required
def put_emails_verify_item(vstring):
    """Update emails item verification from mail."""
    try:

        verification = confirm_email_token(vstring)

        if not verification.result:
            return json_http_response(
                given_message=_(
                    "Token damaged or expired. Email verification"
                    " is impossible."
                ),
                status=400,
                dbg=request.args.get('dbg', False)
            )

        email = Emails.query.filter(
            Emails.id == verification.id
        ).first()

        if email:
            if email.active_until:
                begin_verification_period = email.active_until-timedelta(
                    days=app.config['USER_MAIL_RENEW_NOTIFICATION']
                )
            else:
                begin_verification_period = datetime.now()+timedelta(
                    hours=1
                )

        if email is None:
            return json_http_response(
                status=404,
                given_message=_(
                    "Email with id=%(value)s"
                    " is does not exist in database",
                    value=id
                ),
                dbg=request.args.get('dbg', False)
            )
        elif email.verify and datetime.now() < begin_verification_period:
            return json_http_response(
                status=400,
                given_message=_(
                    "Email with id=%(value)s"
                    " already verified. Request ignored",
                    value=email.id
                ),
                dbg=request.args.get('dbg', False)
            )

        email.verify = True
        email.active_until = datetime.now() + timedelta(
            days=app.config['USER_MAIL_RENEW']
        )

        new_verification_period = email.active_until-timedelta(
            days=app.config['USER_MAIL_RENEW_NOTIFICATION']
        )

        db.session.commit()

        response = json_http_response(
            given_message=_(
                "Email successfully verified! Next verification period begins"
                " from %(period)s",
                period=new_verification_period.strftime("%m-%d %H:%M:%S")
            ),
            status=200,
            dbg=request.args.get('dbg', False)
        )
    except Exception:

        response = json_http_response(dbg=request.args.get('dbg', False))

    return response
