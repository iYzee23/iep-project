from math import ceil
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from sqlalchemy import and_
from web3.exceptions import ContractLogicError
from models import *
from configuration import Configuration
from decorator import roleCheck, web3, bytecode, abi, owner, orderContract
from web3 import Account
import json

application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)


@application.route('/search', methods=['GET'])
@roleCheck("customer")
@jwt_required()
def mSearchProducts():
    product_name = ""
    category_name = ""

    if "name" in request.args:
        product_name = request.args["name"]
    if "category" in request.args:
        category_name = request.args["category"]

    pQuery = Product.query
    if product_name:
        pQuery = pQuery.filter(
            Product.name.like(f"%{product_name}%")
        )
    if category_name:
        pQuery = pQuery.join(
            ProductCategory, Product.id == ProductCategory.product_id
        ).join(
            Category, ProductCategory.category_id == Category.id
        ).filter(
            Category.name.like(f"%{category_name}%")
        )
    products = pQuery.all()

    cQuery = Category.query
    if category_name:
        cQuery = cQuery.filter(
            Category.name.like(f"%{category_name}%")
        )
    if product_name:
        cQuery = cQuery.join(
            ProductCategory, Category.id == ProductCategory.category_id
        ).join(
            Product, ProductCategory.product_id == Product.id
        ).filter(
            Product.name.like(f"%{product_name}%")
        )
    categories = cQuery.distinct(Category.name).all()

    response = {
        "categories": [category.name for category in categories],
        "products": []
    }

    # Populate the response data with product information
    for product in products:
        product_data = {
            "categories": [category.name for category in product.categories],
            "id": product.id,
            "name": product.name,
            "price": product.price
        }
        response["products"].append(product_data)

    return jsonify(response)


# owner --> constructor(customer)
# customer --> function customerPaid()
# customer --> function orderDelivered()
# owner --> function courierJoined(courier)


@application.route('/order', methods=['POST'])
@roleCheck("customer")
@jwt_required()
def mCreateOrder():
    if 'requests' not in request.json:
        return jsonify({
            'message': 'Field requests is missing.'
        }), 400

    price = 0
    requests = request.json['requests']
    for i, req in enumerate(requests):
        if 'id' not in req:
            return jsonify({
                'message': f'Product id is missing for request number {i}.'
            }), 400
        if 'quantity' not in req:
            return jsonify({
                'message': f'Product quantity is missing for request number {i}.'
            }), 400

        product_id = req['id']
        quantity = req['quantity']

        if not isinstance(product_id, int) or product_id <= 0:
            return jsonify({
                'message': f'Invalid product id for request number {i}.'
            }), 400
        if not isinstance(quantity, int) or quantity <= 0:
            return jsonify({
                'message': f'Invalid product quantity for request number {i}.'
            }), 400

        product = Product.query.filter(Product.id == product_id).first()
        if not product:
            return jsonify({
                'message': f'Invalid product for request number {i}.'
            }), 400
        price += product.price * quantity

    if 'address' not in request.json or request.json['address'] == '':
        return jsonify({
            'message': 'Field address is missing.'
        }), 400

    if not web3.is_address(request.json['address']):
        return jsonify({
            'message': 'Invalid address.'
        }), 400

    transaction_hash = orderContract.constructor(request.json['address']).transact({
        "from": owner,
    })
    receipt = web3.eth.wait_for_transaction_receipt(transaction_hash)
    contractAddress = receipt.contractAddress

    order = Order()
    order.email = get_jwt_identity()
    order.contract = contractAddress
    order.price = price
    database.session.add(order)
    database.session.commit()

    requests = request.json['requests']
    for req in requests:
        product_id = req['id']
        quantity = req['quantity']
        product_order = ProductOrder()
        product_order.product_id = product_id
        product_order.order_id = order.id
        product_order.quantity = quantity
        database.session.add(product_order)

    database.session.commit()
    return jsonify({
        'id': order.id
    })


@application.route('/status', methods=['GET'])
@roleCheck("customer")
@jwt_required()
def mGetOrderStatus():
    orders = Order.query.filter(Order.email == get_jwt_identity()).all()

    result = {"orders": []}
    for order in orders:
        order_data = {
            "products": [],
            "price": order.price,
            "status": order.status.value,
            "timestamp": order.timestamp.isoformat()
        }

        for prod in order.products:
            prod_data = {
                "categories": [category.name for category in prod.categories],
                # "id": prod.id,
                "name": prod.name,
                "price": prod.price,
                "quantity": ProductOrder.query.filter(and_(
                    ProductOrder.order_id == order.id,
                    ProductOrder.product_id == prod.id
                )).first().quantity
            }
            order_data["products"].append(prod_data)

        result["orders"].append(order_data)

    return jsonify(result)


@application.route('/delivered', methods=['POST'])
@roleCheck("customer")
@jwt_required()
def mConfirmDelivery():
    if 'id' not in request.json:
        return jsonify({
            "message": "Missing order id."
        }), 400

    order_id = request.json['id']
    if not isinstance(order_id, int) or order_id <= 0:
        return jsonify({
            "message": "Invalid order id."
        }), 400

    order = Order.query.filter(Order.id == order_id).first()
    if not order or order.status != Status.PENDING:
        return jsonify({
            "message": "Invalid order id."
        }), 400

    if 'keys' not in request.json or request.json['keys'] == '':
        return jsonify({
            "message": "Missing keys."
        }), 400

    if 'passphrase' not in request.json or request.json['passphrase'] == '':
        return jsonify({
            "message": "Missing passphrase."
        }), 400

    keys = json.loads(request.json["keys"].replace("'", '"'))
    passphrase = request.json["passphrase"]

    try:
        address = web3.to_checksum_address(keys["address"])
        private_key = Account.decrypt(keys, passphrase).hex()
        currContract = web3.eth.contract(address=order.contract, abi=abi, bytecode=bytecode)

        try:
            transaction = currContract.functions.orderDelivered().build_transaction({
                "from": address,
                "nonce": web3.eth.get_transaction_count(address),
                "gasPrice": web3.eth.gas_price
            })
            signed_transaction = web3.eth.account.sign_transaction(transaction, private_key)
            transaction_hash = web3.eth.send_raw_transaction(signed_transaction.rawTransaction)
            receipt = web3.eth.wait_for_transaction_receipt(transaction_hash)
        except ContractLogicError as error:
            return jsonify({
                "message": str(error)[str(error).find("revert ")+7:]
            }), 400

    except ValueError:
        return jsonify({
            "message": "Invalid credentials."
        }), 400

    order.status = Status.COMPLETE
    database.session.add(order)
    database.session.commit()

    return jsonify()


@application.route('/pay', methods=['POST'])
@roleCheck("customer")
@jwt_required()
def mPay():
    if 'id' not in request.json:
        return jsonify({
            "message": "Missing order id."
        }), 400

    order_id = request.json['id']
    if not isinstance(order_id, int) or order_id <= 0:
        return jsonify({
            "message": "Invalid order id."
        }), 400

    order = Order.query.filter(Order.id == order_id).first()
    if not order:
        return jsonify({
            "message": "Invalid order id."
        }), 400

    if 'keys' not in request.json or request.json['keys'] == '':
        return jsonify({
            "message": "Missing keys."
        }), 400

    if 'passphrase' not in request.json or request.json['passphrase'] == '':
        return jsonify({
            "message": "Missing passphrase."
        }), 400

    keys = json.loads(request.json["keys"].replace("'", '"'))
    passphrase = request.json["passphrase"]

    try:
        address = web3.to_checksum_address(keys["address"])
        private_key = Account.decrypt(keys, passphrase).hex()
        currContract = web3.eth.contract(address=order.contract, abi=abi, bytecode=bytecode)

        try:
            transaction = currContract.functions.customerPaid().build_transaction({
                "from": address,
                "value": ceil(order.price),
                "nonce": web3.eth.get_transaction_count(address),
                "gasPrice": web3.eth.gas_price
            })
            signed_transaction = web3.eth.account.sign_transaction(transaction, private_key)
            transaction_hash = web3.eth.send_raw_transaction(signed_transaction.rawTransaction)
            receipt = web3.eth.wait_for_transaction_receipt(transaction_hash)
        except ContractLogicError as error:
            if "Transfer already complete." not in str(error):
                return jsonify({
                    "message": f"Insufficient funds."
                }), 400
            else:
                return jsonify({
                    "message": str(error)[str(error).find("revert ")+7:]
                }), 400

    except ValueError:
        return jsonify({
            "message": "Invalid credentials."
        }), 400

    return jsonify()


if __name__ == "__main__":
    database.init_app(application)
    # application.run(debug=True, port="5002")
    application.run(debug=True, host="0.0.0.0")
