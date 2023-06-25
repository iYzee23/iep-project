from functools import wraps
from flask_jwt_extended import get_jwt, verify_jwt_in_request, get_jwt_identity
from flask import jsonify
from redis import Redis
from configuration import Configuration
from web3 import Web3, HTTPProvider
import os


def read_file(path):
    with open(path, "r") as file:
        return file.read()


def roleCheck(role_name):
    def innerRole(function):
        @wraps(function)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if "role_name" in claims and role_name in claims["role_name"]:
                email = get_jwt_identity()
                with Redis(host=Configuration.REDIS_HOST) as redis:
                    if redis.exists(email):
                        return jsonify({
                            "msg": "Permission denied!"
                        }), 403
                return function(*args, **kwargs)
            else:
                return jsonify({
                    "msg": "Missing Authorization Header"
                }), 401
        return decorator
    return innerRole


web3 = Web3(HTTPProvider(f"http://{Configuration.BLOCKCHAIN_URL}:8545"))

bytecode = read_file("./OrderContract.bin")
abi = read_file("./OrderContract.abi")

orderContract = web3.eth.contract(bytecode=bytecode, abi=abi)
owner = web3.eth.accounts[0]
