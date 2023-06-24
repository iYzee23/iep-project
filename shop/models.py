from flask_sqlalchemy import SQLAlchemy
import enum
import datetime

database = SQLAlchemy()


class Status(enum.Enum):
    CREATED = "CREATED"
    PENDING = "PENDING"
    COMPLETE = "COMPLETE"


class ProductOrder(database.Model):
    __tablename__ = "product_order_table"
    id = database.Column(database.Integer, primary_key=True)
    quantity = database.Column(database.Integer, nullable=False)
    product_id = database.Column(database.Integer, database.ForeignKey("product_table.id"), nullable=False)
    order_id = database.Column(database.Integer, database.ForeignKey("order_table.id"), nullable=False)


class Order(database.Model):
    __tablename__ = "order_table"
    id = database.Column(database.Integer, primary_key=True)
    price = database.Column(database.Float, nullable=False)
    status = database.Column(database.Enum(Status), nullable=False, default=Status.CREATED)
    timestamp = database.Column(database.DateTime, nullable=False, default=datetime.datetime.utcnow)
    email = database.Column(database.String(256), nullable=False)

    products = database.relationship("Product", secondary=ProductOrder.__table__, back_populates="orders")


class ProductCategory(database.Model):
    __tablename__ = "product_category_table"
    id = database.Column(database.Integer, primary_key=True)
    product_id = database.Column(database.Integer, database.ForeignKey("product_table.id"), nullable=False)
    category_id = database.Column(database.Integer, database.ForeignKey("category_table.id"), nullable=False)


class Category(database.Model):
    __tablename__ = "category_table"
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False, unique=True)

    products = database.relationship("Product", secondary=ProductCategory.__table__, back_populates="categories")


class Product(database.Model):
    __tablename__ = "product_table"
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False, unique=True)
    price = database.Column(database.Float, nullable=False)

    categories = database.relationship("Category", secondary=ProductCategory.__table__, back_populates="products")
    orders = database.relationship("Order", secondary=ProductOrder.__table__, back_populates="products")

    def __init__(self, name, price):
        self.name = name
        self.price = price
