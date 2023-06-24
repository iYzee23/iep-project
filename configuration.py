import os


redisHost = os.environ["REDIS_HOST"] if "REDIS_HOST" in os.environ else "localhost"


class Configuration:
    REDIS_HOST = redisHost
