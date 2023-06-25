from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required
from models import *
from configuration import Configuration
from decorator import roleCheck, web3, bytecode, abi, owner, orderContract
from web3.exceptions import ContractLogicError

application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)


@application.route('/orders_to_deliver', methods=['GET'])
@roleCheck("courier")
@jwt_required()
def mGetOrdersToDeliver():
    orders = Order.query.filter(Order.status == Status.CREATED).all()
    orders_data = [{"id": order.id, "email": order.email} for order in orders]

    return jsonify({
        "orders": orders_data
    })


# owner --> constructor(customer)
# customer --> function customerPaid()
# customer --> function orderDelivered()
# owner --> function courierJoined(courier)


@application.route('/pick_up_order', methods=['POST'])
@roleCheck("courier")
@jwt_required()
def mPickupOrder():
    if 'id' not in request.json:
        return jsonify({
            'message': 'Missing order id.'
        }), 400

    order_id = request.json['id']
    if not isinstance(order_id, int) or order_id <= 0:
        return jsonify({
            'message': 'Invalid order id.'
        }), 400

    order = Order.query.filter(Order.id == order_id).first()
    if not order or order.status != Status.CREATED:
        return jsonify({
            'message': 'Invalid order id.'
        }), 400

    if 'address' not in request.json or request.json['address'] == '':
        return jsonify({
            'message': 'Missing address.'
        }), 400

    if not web3.is_address(request.json['address']):
        return jsonify({
            'message': 'Invalid address.'
        }), 400

    try:
        currContract = web3.eth.contract(address=order.contract, abi=abi, bytecode=bytecode)
        transaction_hash = currContract.functions.courierJoined(request.json['address']).transact({
            "from": owner
        })
        receipt = web3.eth.wait_for_transaction_receipt(transaction_hash)
    except ContractLogicError as error:
        return jsonify({
            "message": str(error)[str(error).find("revert ")+7:]
        }), 400

    order.status = Status.PENDING
    database.session.add(order)
    database.session.commit()

    return jsonify()


if __name__ == "__main__":
    database.init_app(application)
    # application.run(debug=True, port="5003")
    application.run(debug=True, host="0.0.0.0")
