from json import loads
from os import listdir, path, getenv
from sys import stdout

from dotenv import load_dotenv
from elasticsearch import Elasticsearch


# Define some console colors.
class Colors:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# Load the environment variables from .env file.
load_dotenv()

# Get Elastic Search host and data path.
ELASTIC_SEARCH_HOST = getenv("ELASTIC_SEARCH_HOST")
DATA_PATH = getenv("DATA_PATH")

# Define Elastic Search instance.
es = Elasticsearch(ELASTIC_SEARCH_HOST)

# Get all the JSON files from data folder.
file_names = [file_name for file_name in listdir(DATA_PATH) if file_name.endswith(".json")]

print(f"\n{Colors.BOLD}▶ Creating new indices{Colors.ENDC}")

for file_name in file_names:
    index = path.splitext(file_name)[0]

    if es.indices.exists(index):
        es.indices.delete(index)

    # Create an indices for each JSON file.
    with open(path.join(DATA_PATH, file_name), "r") as open_file:
        index = path.splitext(file_name)[0]

        es.indices.create(index=index, body="""{
            "mappings": {
                "properties": {
                    "content": { 
                        "type": "text",
                        "fields": {
                            "length": { 
                                "type": "token_count",
                                "analyzer": "english"
                            }
                        }
                    }
                }
            }
        }""")

        for id, line in enumerate(open_file):
            es.index(index=index, id=id, body=loads(line))
            stdout.write(f"\r[{Colors.FAIL}x{Colors.ENDC}] {index} {int(id / 1024 * 100)}%")
            stdout.flush()

        stdout.write("\r")
        print(f"[{Colors.OKGREEN}✓{Colors.ENDC}] {index}")
