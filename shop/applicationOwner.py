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
            'message': 'Field file is missing.'
        }), 400

    content = request.files["file"].stream.read().decode("utf-8")
    stream = io.StringIO(content)
    reader = csv.reader(stream)
    products = []
    line_number = 0
    existing_products = set()

    incorrect_price_indicator = -1
    product_already_exists_indicator = ""

    for row in reader:
        print(row)
        if len(row) != 3:
            return jsonify({
                'message': f'Incorrect number of values on line {line_number}.'
            }), 400

        categories, name, price = row
        try:
            if float(price) <= 0:
                if incorrect_price_indicator == -1:
                    incorrect_price_indicator = line_number
        except Exception:
            if incorrect_price_indicator == -1:
                incorrect_price_indicator = line_number

        if name in existing_products or Product.query.filter(Product.name == name).first():
            if not product_already_exists_indicator:
                product_already_exists_indicator = name
        existing_products.add(name)

        products.append((categories, name, price))
        line_number += 1

    if incorrect_price_indicator != -1:
        return jsonify({
            'message': f'Incorrect price on line {incorrect_price_indicator}.'
        }), 400

    if product_already_exists_indicator:
        return jsonify({
            'message': f'Product {product_already_exists_indicator} already exists.'
        }), 400

    for categories, name, price in products:
        prod = Product(name=name, price=price)
        database.session.add(prod)
        database.session.commit()

        for category in categories.split("|"):
            cat = Category.query.filter(Category.name == category).first()
            if not cat:
                cat = Category()
                cat.name = category
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
    f1 = func.sum(func.IF(
        Order.status == Status.COMPLETE,
        ProductOrder.quantity, 0)
    )
    f2 = func.sum(func.IF(
        or_(Order.status == Status.CREATED, Order.status == Status.PENDING),
        ProductOrder.quantity, 0)
    )

    statistics = database.session.query(
        Product.name, f1, f2
    ).join(
        ProductOrder, Product.id == ProductOrder.product_id
    ).join(
        Order, ProductOrder.order_id == Order.id
    ).group_by(
        Product.name
    ).having(
        f1 > 0
    ).order_by(
        Product.name
    ).all()

    result = {"statistics": []}
    for name, sold, waiting in statistics:
        result["statistics"].append({"name": name, "sold": int(sold), "waiting": int(waiting)})

    return jsonify(result)


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
    application.run(debug=True, port="5001")
    # application.run(debug=True, host="0.0.0.0")
