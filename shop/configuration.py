from datetime import timedelta
import os


databaseUrl = os.environ["DATABASE_URL"] if "DATABASE_URL" in os.environ else "localhost"
redisHost = os.environ["REDIS_HOST"] if "REDIS_HOST" in os.environ else "localhost"


class Configuration:
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{databaseUrl}/shop"
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    # JWT_REFRESH_TOKEN_EXPIRES = timedelta(hours=1)
    REDIS_HOST = redisHost
