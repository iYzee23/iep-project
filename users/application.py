from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import and_
from models import *
from configuration import Configuration
from redis import Redis
import re

application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)


def checkEmail(email):
    pattern = r'^\w+@[a-zA-Z_]+?\.[a-zA-Z]{2,3}$'
    return re.match(pattern, email) is not None


@application.route("/register_customer", methods=["POST"])
@application.route("/register_courier", methods=["POST"])
def mRegister():
    if "forename" not in request.json or not request.json["forename"]:
        return jsonify({
            'message': f'Field forename is missing.'
        }), 400
    if "surname" not in request.json or not request.json["surname"]:
        return jsonify({
            'message': f'Field surname is missing.'
        }), 400
    if "email" not in request.json or not request.json["email"]:
        return jsonify({
            'message': f'Field email is missing.'
        }), 400
    if "password" not in request.json or not request.json["password"]:
        return jsonify({
            'message': f'Field password is missing.'
        }), 400

    email = request.json["email"]
    password = request.json["password"]
    forename = request.json["forename"]
    surname = request.json["surname"]

    if not checkEmail(email) or len(email) > 256:
        return jsonify({
            'message': 'Invalid email.'
        }), 400

    if len(password) < 8 or len(password) > 256:
        return jsonify({
            'message': 'Invalid password.'
        }), 400

    if User.query.filter(User.email == email).first():
        return jsonify({
            'message': 'Email already exists.'
        }), 400

    # role = Role.query.filter(Role.name == "customer").first()
    role = "customer" if request.path == "/register_customer" else "courier"
    user = User(
        email=email,
        password=password,
        forename=forename,
        surname=surname,
        role_name=role
    )
    database.session.add(user)
    database.session.commit()

    with Redis(host=Configuration.REDIS_HOST) as redis:
        if redis.exists(email):
            redis.delete(email)

    return jsonify()


@application.route("/login", methods=["POST"])
def mLogin():
    if "email" not in request.json or not request.json["email"]:
        return jsonify({
            'message': f'Field email is missing.'
        }), 400
    if "password" not in request.json or not request.json["password"]:
        return jsonify({
            'message': f'Field password is missing.'
        }), 400

    email = request.json["email"]
    password = request.json["password"]

    if not checkEmail(email) or len(email) > 256:
        return jsonify({
            'message': 'Invalid email.'
        }), 400

    user = User.query.filter(and_(User.email == email, User.password == password)).first()
    if not user:
        return jsonify({
            'message': 'Invalid credentials.'
        }), 400

    additionalClaims = {
        "forename": user.forename,
        "surname": user.surname,
        "email": user.email,
        "password": user.password,
        "role_name": user.role_name
    }
    accessToken = create_access_token(identity=user.email, additional_claims=additionalClaims)
    # refreshToken = create_refresh_token(identity=user.email, additional_claims=additionalClaims)

    return jsonify({
        'accessToken': accessToken
    })


@application.route("/delete", methods=["POST"])
@jwt_required()
def mDelete():
    userMail = get_jwt_identity()

    user = User.query.filter(User.email == userMail).first()
    if not user:
        return jsonify({
            'message': 'Unknown user.'
        }), 400

    database.session.delete(user)
    database.session.commit()

    with Redis(host=Configuration.REDIS_HOST) as redis:
        redis.set(userMail, "", ex=3600)

    return jsonify()


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True)
    # application.run(debug=True, host="0.0.0.0")
