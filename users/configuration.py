from datetime import timedelta
import os


databaseUrl = os.environ["DATABASE_URL"]


class Configuration:
    # SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@localhost/users"
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{databaseUrl}/users"
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    # JWT_REFRESH_TOKEN_EXPIRES = timedelta(hours=1)
    # REDIS_HOST = "localhost"
    REDIS_HOST = os.environ["REDIS_HOST"]
