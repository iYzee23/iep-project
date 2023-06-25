import os


redisHost = os.environ["REDIS_HOST"] if "REDIS_HOST" in os.environ else "localhost"
blockChainUrl = os.environ["BLOCKCHAIN_URL"] if "BLOCKCHAIN_URL" in os.environ else "localhost"


class Configuration:
    REDIS_HOST = redisHost
    BLOCKCHAIN_URL = blockChainUrl
