"""Views of API version 1.0.0: User profile."""

from flask import Response, json, request

from .blueprint import APIv1_0_0

from .utils import password_generator, json_http_response


@APIv1_0_0.route('/profile/<int:uid>', methods=['GET'])
# @token_required
# def get_profile_by_id(current_user, uid):
def get_profile_by_id(uid):
    """Get user profile by id."""
    try:

        password = password_generator()
        udata = {"login": "Goomba", "password": password, "uid": uid}

        response = Response(
            response=json.dumps(udata),
            status=200,
            mimetype='application/json'
        )

    except Exception:

        response = json_http_response(dbg=request.args.get('dbg', False))

    return response
