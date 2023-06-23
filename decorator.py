from functools import wraps
from flask_jwt_extended import get_jwt
from flask import jsonify


def roleCheck(role_name):
    def innerRole(function):
        @wraps(function)
        def decorator(*args, **kwargs):
            claims = get_jwt()
            if "role_name" in claims and role_name in claims["role_name"]:
                return function(*args, **kwargs)
            else:
                return jsonify({
                    "msg": "Permission denied!"
                }), 403
        return decorator
    return innerRole
