import logging
import os
import shutil
import subprocess
import tempfile
from pymongo import MongoClient
#from aws_lambda_powertools import Logger

from crawlers.base import BaseCrawler
from documents import RepositoryDocument
from config import settings
#logger = Logger(service="decodingml/crawler")

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("debug.log"),
                        logging.StreamHandler()
                    ])

class GithubCrawler(BaseCrawler):
    model = RepositoryDocument

    def __init__(self, ignore=(".git", ".toml", ".lock", ".png")) -> None:
        super().__init__()
        self._ignore = ignore

        #configure mongodb connection
        self.mongo_client = MongoClient(settings.DATABASE_HOST)
        self.db_name = settings.DATABASE_NAME
        self.collection_name = "repositories"

    def extract(self, link: str, **kwargs) -> None:
        #logger.info(f"Starting scrapping GitHub repository: {link}")
        logging.info(f"Starting scrapping GitHub repository: {link}")

        repo_name = link.rstrip("/").split("/")[-1]

        local_temp = tempfile.mkdtemp()
        print(local_temp)
        print(os.getcwd())
        try:
            os.chdir(local_temp)
            subprocess.run(["git", "clone", link])

            logging.info(f"Cloned {link} into {local_temp}")

            repo_path = os.path.join(local_temp, os.listdir(local_temp)[0])

            tree = {}
            for root, dirs, files in os.walk(repo_path):
                dir = root.replace(repo_path, "").lstrip("/")
                if dir.startswith(self._ignore):
                    continue

                for file in files:
                    if file.endswith(self._ignore):
                        continue
                    file_path = os.path.join(dir, file)
                    with open(os.path.join(root, file), "r", errors="ignore") as f:
                        tree[file_path] = f.read().replace(" ", "")

            print(tree)
            # save to mongodb
            db = self.mongo_client[self.db_name]
            collection = db[self.collection_name]
            document = {
                "name": repo_name,
                "link": link,
                "content": tree,
                "owner_id": kwargs.get("user")
            }
            result = collection.insert_one(document)

            instance = self.model(
                name=repo_name, link=link, content=tree, owner_id=kwargs.get("user")
            )
            print(instance)
            instance.save(collection=collection)
            logging.info(f"Saved GitHub repository: {link}")

        except Exception as e:
            logging.exception(f"An error occurred while scrapping GitHub repository: {e}")
            raise
        finally:
            shutil.rmtree(local_temp)
            logging.info(f"Deleted temporary directory {local_temp}")
        #logger.info(f"Finished scrapping GitHub repository: {link}")
