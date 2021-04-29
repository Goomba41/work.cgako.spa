"""Views of API version 1.0.0: System modules and modules types."""

from flask import request, Response, json, url_for, render_template, \
    current_app as app
from flask_babel import _
from flask_mail import Message
from app import db, mail

from .blueprint import APIv1_0_0
from app.models import Emails
from app.schemas import EmailsSchema
from .utils import json_http_response, marshmallow_excluding_converter, \
     marshmallow_only_fields_converter, sqlalchemy_filters_converter, \
     sqlalchemy_orders_converter, pagination_of_list, variable_type_check, \
     generate_confirmation_token, confirm_email_token, display_time


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
        print(f"UPDATE EMAIL {id}")
        response = json_http_response(
            status=200,
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

        print(app.config['USER_MAIL_RENEW'])
        print(app.config['USER_MAIL_RENEW_NOTIFICATION'])

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
        elif recipient.verify:
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
        confirm_url = 'http://192.168.0.89:8080/verify/mail/'
        confirm_url += token.decode("utf-8")

        html = render_template(
            'confirmation_mail.html',
            confirm_url=confirm_url,
            active_time="".join(display_time(expiration))
        )
        subject = 'Подтверждение адреса электронной почты в CMS сайта ЦГАКО'

        message = Message(
            subject,
            html=html,
            recipients=[recipient.value],
            sender=app.config['MAIL_DEFAULT_SENDER']
        )

        # mail.send(message)

        # print(confirm_email_token(token))
        response = json_http_response(
            given_message=_(
                "Mail successfully send to recipient for verification"
            ),
            status=200,
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
        print("UPDATE EMAIL VERIFICATION")
        response = json_http_response(
            status=200,
            dbg=request.args.get('dbg', False)
        )
    except Exception:

        response = json_http_response(dbg=request.args.get('dbg', False))

    return response
