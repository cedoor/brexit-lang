from os import path, getenv
from time import time

from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from pyspark.ml.feature import Tokenizer
from pyspark.sql import SparkSession, Row


# Define some console colors.
class Colors:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def analyze_newspaper(articles, name):
    # Tokenize content article field.
    tokenizer = Tokenizer(inputCol="content", outputCol="tokens")
    articles = tokenizer.transform(articles)

    all_tokens = articles.rdd.flatMap(lambda article: article.tokens)
    token_occurrences = all_tokens.map(lambda token: (token, 1)).reduceByKey(lambda x, y: x + y)

    word_occurrences = token_occurrences.filter(lambda x: x[0] in WORDS_TO_ANALYZE).sortBy(lambda x: x[0])

    print(f"\n# {Colors.OKGREEN}{name}{Colors.ENDC}:")

    number_of_tokens = all_tokens.count()

    for word_occurrence in word_occurrences.collect():
        occurrence = round(word_occurrence[1] / number_of_tokens * 1000, 3)

        print(f" {Colors.OKBLUE}{word_occurrence[0]}{Colors.ENDC}: {occurrence}")


def list_to_data_frame(_list):
    row = Row(*_list[0])

    return spark.createDataFrame([row(*x.values()) for x in _list])


def get_newspaper_articles(name):
    articles = es.search(index=name, body="""{
        "size": 1028,
        "_source": ["content"],
        "query": { "match_all": {} }
    }""")

    return [article["_source"] for article in articles["hits"]["hits"]]


# Load the environment variables from .env file.
load_dotenv()

# Get environment variables.
ELASTIC_SEARCH_HOST = getenv("ELASTIC_SEARCH_HOST")
DATA_FILES = getenv("DATA_FILES").split(" ")
WORDS_TO_ANALYZE = getenv("WORDS_TO_ANALYZE").split(" ")

# Define Elastic Search instance.
es = Elasticsearch(ELASTIC_SEARCH_HOST)

# Define Spark context.
spark = SparkSession.builder.master("local[*]").getOrCreate()
sc = spark.sparkContext

# Set Spark log level to error (it will show only error messages).
sc.setLogLevel("ERROR")

# Get all newspaper's names.
newspaper_names = [path.splitext(file_name)[0] for file_name in DATA_FILES]

# Get all the articles of each newspaper.
newspaper_articles = [(name, list_to_data_frame(get_newspaper_articles(name))) for name in newspaper_names]

start = time()

print(f"\n{Colors.BOLD}▶ Word occurrences:{Colors.ENDC}")

# Analyze the newspapers (Spark Analysis).
for name, articles in newspaper_articles:
    analyze_newspaper(articles, name)

end = time()

print(f"\n{Colors.BOLD}▶ Execution time:{Colors.ENDC} {round(end - start, 3)}")
