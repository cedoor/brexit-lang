import json
from os import path, getenv
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


def save_data(file_name, data):
    with open("./" + file_name + ".json", "w") as fp:
        json.dump(data, fp, indent=4, ensure_ascii=False)

    print(f"\n{Colors.OKGREEN}✔ Results saved in {file_name}.json file!{Colors.ENDC}")


# Load the environment variables from .env file.
load_dotenv()

# Get environment variables.
ELASTIC_SEARCH_HOST = getenv("ELASTIC_SEARCH_HOST")
DATA_FILES = getenv("DATA_FILES").split(" ")
WORDS_TO_ANALYZE = getenv("WORDS_TO_ANALYZE").split(" ")

# Define Elastic Search instance.
es = Elasticsearch(ELASTIC_SEARCH_HOST)

# Get all newspaper's names for Elastic Search indices.
newspaper_indices = [path.splitext(file_name)[0] for file_name in DATA_FILES]

print(f"\n{Colors.BOLD}▶ Word occurrences:{Colors.ENDC}")

start = time()

for index in newspaper_indices:
    print(f"\n# {Colors.OKGREEN}{index}{Colors.ENDC}:")

    results = {
        "number_of_tokens": 0,
        "word_occurrences": {}
    }

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

        number_of_tokens = aggregation_response["aggregations"]["number_of_tokens"]["value"]

        results["number_of_tokens"] = number_of_tokens

        word_statistics = term_vector_response["term_vectors"]["content"]["terms"][word]

        if "ttf" in word_statistics:
            total_term_frequency = term_vector_response["term_vectors"]["content"]["terms"][word]["ttf"]
            normalized_occurrences = round(total_term_frequency / number_of_tokens * 1000, 3)

            results["word_occurrences"][word] = normalized_occurrences

            print(f" {Colors.OKBLUE}{word}{Colors.ENDC}: {normalized_occurrences}")

    save_data(index, results)

end = time()

print(f"\n{Colors.BOLD}▶ Execution time:{Colors.ENDC} {round(end - start, 3)}")
