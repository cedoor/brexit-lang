from os import listdir, path, getenv
from time import time

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

# Get environment variables.
ELASTIC_SEARCH_HOST = getenv("ELASTIC_SEARCH_HOST")
DATA_PATH = getenv("DATA_PATH")
WORDS_TO_ANALYZE = getenv("WORDS_TO_ANALYZE").split(" ")

# Define Elastic Search instance.
es = Elasticsearch(ELASTIC_SEARCH_HOST)

# Get all the JSON files from data folder to retrieve Elastic Search indices.
indices = [path.splitext(file_name)[0] for file_name in listdir(DATA_PATH) if file_name.endswith(".json")]

start = time()

print(f"\n{Colors.BOLD}▶ Word occurrences:{Colors.ENDC}")

for index in indices:
    print(f"\n# {Colors.OKGREEN}{index}{Colors.ENDC}:")

    for word in WORDS_TO_ANALYZE:
        term_vector_response = es.termvectors(index=index, body="""{
            "doc": { "content": "%s" },
            "fields" : ["content"],
            "term_statistics" : true,
            "field_statistics" : true
        }""" % word)

        aggregation_response = es.search(index=index, body="""{   
            "size": 0,
            "aggs" : {
                "number_of_tokens" : { "sum" : { "field" : "content.length" } }
            }
        }""")

        total_terms = aggregation_response["aggregations"]["number_of_tokens"]["value"]
        total_term_frequency = term_vector_response["term_vectors"]["content"]["terms"][word]["ttf"]

        print(f" {Colors.OKBLUE}{word}{Colors.ENDC}: {round(total_term_frequency / total_terms * 1000, 3)}")

end = time()

print(f"\n{Colors.BOLD}▶ Execution time:{Colors.ENDC} {round(end - start, 3)}")
