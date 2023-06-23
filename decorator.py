from functools import wraps
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from flask import jsonify


def roleCheck(role_name):
    def innerRole(function):
        @wraps(function)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if "role_name" in claims and role_name in claims["role_name"]:
                return function(*args, **kwargs)
            else:
                # return jsonify({
                #     "msg": "Permission denied!"
                # }), 403
                return jsonify({
                    "msg": "Missing Authorization Header"
                }), 401
        return decorator
    return innerRole
