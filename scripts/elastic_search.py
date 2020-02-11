from json import loads
from os import listdir, path
from sys import argv, stdout
from time import sleep

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


# Define all words to search in the articles.
words = [
    "but",
    "although",
    "brexit",
    "free",
    "we",
    "should",
    "can"
]

# Get the arguments (Elastic Search host and data path).
[host, data_path] = argv[1:3]

# Get all the JSON files from data folder.
file_names = [file_name for file_name in listdir(data_path) if file_name.endswith(".json")]

# Define Elastic Search instance.
es = Elasticsearch(host)

if es.indices.exists("the_guardian") is False:
    print(f"\n{Colors.BOLD}▶ Removing existing indices{Colors.ENDC}...")

    for file_name in file_names:
        index = path.splitext(file_name)[0]
        if es.indices.exists(index):
            es.indices.delete(index)

    print(f"\n{Colors.BOLD}▶ Creating indices{Colors.ENDC}...")

    # Create an indices for each JSON file.
    for file_name in file_names:
        with open(path.join(data_path, file_name), "r") as open_file:
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

    # Wait two seconds for next analysis.
    sleep(2)

print(f"\n{Colors.BOLD}▶ Word occurrences:{Colors.ENDC}")

for word in words:
    print(f"\n`{Colors.OKGREEN}{word}{Colors.ENDC}` analysis:")

    for file_name in file_names:
        index = path.splitext(file_name)[0]

        res1 = es.termvectors(index=index, body="""{
            "doc": { "content": "%s" },
            "fields" : ["content"],
            "term_statistics" : true,
            "field_statistics" : true
        }""" % word)

        res2 = es.search(index=index, body="""{   
            "size": 0,
            "aggs" : {
                "number_of_tokens" : { "sum" : { "field" : "content.length" } }
            }
        }""")

        number_of_tokens = res2["aggregations"]["number_of_tokens"]["value"]

        ttf = res1["term_vectors"]["content"]["terms"][word]["ttf"]

        print(f"{Colors.OKBLUE}{index}{Colors.ENDC}: {ttf / number_of_tokens * 1000}")
