from flask import Flask
from flask_migrate import Migrate, init, migrate, upgrade
from sqlalchemy_utils import database_exists, create_database
from models import *
from configuration import Configuration

application = Flask(__name__)
application.config.from_object(Configuration)

migrateObject = Migrate(application, database)

done = False
while not done:
    try:
        if not database_exists(application.config["SQLALCHEMY_DATABASE_URI"]):
            create_database(application.config["SQLALCHEMY_DATABASE_URI"])
        database.init_app(application)

        with application.app_context() as context:
            init()
            migrate(message="Initial migration")
            upgrade()

            roleOwner = Role()
            roleCustomer = Role()
            roleCourier = Role()

            roleOwner.name = "owner"
            roleCustomer.name = "customer"
            roleCourier.name = "courier"

            database.session.add(roleOwner)
            database.session.add(roleCustomer)
            database.session.add(roleCourier)
            database.session.commit()

            owner = User(
                email="onlymoney@gmail.com",
                password="evenmoremoney",
                forename="Scrooge",
                surname="McDuck",
                role_name="owner"
            )

            database.session.add(owner)
            database.session.commit()
            done = True
    except Exception as error:
        print(error)
