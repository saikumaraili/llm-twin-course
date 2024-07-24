#from aws_lambda_powertools import Logger
import logging
from config import settings
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

#logger = Logger(service="decodingml/crawler")
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("debug.log"),
                        logging.StreamHandler()
                    ])


class MongoDatabaseConnector:
    _instance: MongoClient | None = None

    def __new__(cls, *args, **kwargs) -> MongoClient:
        if cls._instance is None:
            try:
                cls._instance = MongoClient(settings.DATABASE_HOST)
            except ConnectionFailure as e:
                #logger.error(f"Couldn't connect to the database: {str(e)}")
                logging.error(f"Couldn't connect to the database: {str(e)}")
                raise

        #logger.info(
        #    f"Connection to database with uri: {settings.DATABASE_HOST} successful"
        #)
        logging.info(
            f"Connection to database with uri: {settings.DATABASE_HOST} successful"
        )
        return cls._instance

    def close(self):
        if self._instance:
            self._instance.close()
            #logger.info("Connected to database has been closed.")
            logging.info("Connected to database has been closed.")


connection = MongoDatabaseConnector()
