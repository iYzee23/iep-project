from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required
from sqlalchemy import or_, func
from models import *
from configuration import Configuration
from decorator import roleCheck
import csv
import io

application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)


@application.route('/update', methods=['POST'])
@roleCheck("owner")
@jwt_required()
def mUpdate():
    if 'file' not in request.files:
        return jsonify({
            'message': 'Field file missing.'
        }), 400

    content = request.files["file"].stream.read().decode("utf-8")
    stream = io.StringIO(content)
    reader = csv.reader(stream)
    products = []
    line_number = 0
    existing_products = set()

    for row in reader:
        if len(row) != 3:
            return jsonify({
                'message': f'Incorrect number of values on line {line_number}.'
            }), 400

        categories, name, price = row
        try:
            price = float(price)
            if price <= 0:
                return jsonify({
                    'message': f'Incorrect price on line {line_number}.'
                }), 400
        except ValueError:
            return jsonify({
                'message': f'Incorrect price on line {line_number}.'
            }), 400

        if name in existing_products or Product.query.filter(Product.name == name).first():
            return jsonify({
                'message': f'Product {name} already exists.'
            }), 400
        existing_products.add(name)

        products.append((categories, name, price))
        line_number += 1

    for categories, name, price in products:
        prod = Product(name=name, price=price)
        database.session.add(prod)
        database.session.commit()

        for category in categories.split("|"):
            cat = Category.query.filter(Category.name == category).first()
            if not cat:
                cat = Category()
                cat.name = name
                database.session.add(cat)
                database.session.commit()
            prod_cat = ProductCategory()
            prod_cat.product_id = prod.id
            prod_cat.category_id = cat.id
            database.session.add(prod_cat)

    database.session.commit()
    return jsonify()


@application.route('/product_statistics', methods=['GET'])
@roleCheck("owner")
@jwt_required()
def mGetProductStatistics():
    statistics = database.session.query(
        Product.name,
        func.sum(func.IF(
            Order.status == Status.COMPLETE,
            ProductOrder.quantity, 0)
        ),
        func.sum(func.IF(
            or_(Order.status == Status.CREATED, Order.status == Status.PENDING),
            ProductOrder.quantity, 0)
        )
    ).join(
        ProductOrder, Product.id == ProductOrder.product_id
    ).join(
        Order, ProductOrder.order_id == Order.id
    ).group_by(
        Product.name
    ).order_by(
        Product.name
    ).all()

    result = {"statistics": []}
    for name, sold, waiting in statistics:
        result["statistics"].append({"name": name, "sold": sold, "waiting": waiting})

    return jsonify(result), 200


@application.route('/category_statistics', methods=['GET'])
@roleCheck("owner")
@jwt_required()
def mGetCategoryStatistics():
    f = func.sum(func.IF(
        Order.status == Status.COMPLETE,
        ProductOrder.quantity, 0
    ))

    statistics = database.session.query(
        Category.name, f
    ).join(
        ProductCategory, Category.id == ProductCategory.category_id
    ).join(
        Product, ProductCategory.product_id == Product.id
    ).join(
        ProductOrder, Product.id == ProductOrder.product_id
    ).join(
        Order, ProductOrder.order_id == Order.id
    ).group_by(
        Category.name
    ).order_by(
        f.desc(), Category.name
    ).all()

    result = {"statistics": [category for category, cnt in statistics]}

    return jsonify(result), 200


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0")
