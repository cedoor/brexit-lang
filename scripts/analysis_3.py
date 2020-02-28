import json
from os import path, getenv
from time import time

from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from nltk import download, word_tokenize, sent_tokenize
from pyspark.sql import SparkSession

download('punkt')
download('wordnet')
download('omw')
download('averaged_perceptron_tagger')


# Define some console colors.
class Colors:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def categorize_words(words):
    common_words = []
    contextual_words = []

    for word in words:
        word_components = word.split(":")

        if len(word_components) == 1:
            common_words.append(word)
        else:
            contextual_words.append({
                "word": word_components[0],
                "included": word_components[1].split(","),
                "excluded": word_components[2].split(",")
            })

    return {
        "common": common_words,
        "contextual": contextual_words
    }


def is_contextualized(sentence, contextual_words):
    for contextual_word in contextual_words:
        if contextual_word["word"] in sentence:
            return (any(token in contextual_word["included"] for token in sentence) and
                    all(token not in contextual_word["excluded"] for token in sentence))

    return False


def get_contextual_word(sentence, contextual_words):
    for contextual_word in contextual_words:
        if contextual_word["word"] in sentence:
            return contextual_word["word"]

    return ""


def save_data(file_name, data):
    with open("./" + file_name + ".json", "w") as fp:
        json.dump(data, fp, indent=4, ensure_ascii=False)

    print(f"\n{Colors.OKGREEN}Results saved in {file_name}.json file!{Colors.ENDC}")


def analyze_newspaper(name, articles, words):
    all_tokens = articles.rdd.flatMap(lambda article: word_tokenize(article.content.lower()))
    token_occurrences = all_tokens.map(lambda token: (token, 1)).reduceByKey(lambda x, y: x + y)
    token_occurrences = token_occurrences.filter(lambda x: x[0] in words["common"]).sortBy(lambda x: x[0])

    all_sentences = articles.rdd.flatMap(lambda article: sent_tokenize(article.content.lower()))
    all_sentences = all_sentences.map(lambda sentence: word_tokenize(sentence))
    sentence_occurrences = all_sentences.filter(lambda sentence: is_contextualized(sentence, words["contextual"]))
    sentence_occurrences = sentence_occurrences.map(
        lambda sentence: (get_contextual_word(sentence, words["contextual"]), 1)).reduceByKey(lambda x, y: x + y)

    print(f"\n#### {Colors.OKGREEN}{name}{Colors.ENDC}:")

    number_of_tokens = all_tokens.count()

    results = {
        "number_of_tokens": number_of_tokens,
        "word_occurrences": {}
    }

    for word in token_occurrences.collect() + sentence_occurrences.collect():
        normalized_occurrences = round(word[1] / number_of_tokens * 1000, 3)

        results["word_occurrences"][word[0]] = normalized_occurrences

        print(f"* {Colors.OKBLUE}{word[0]}{Colors.ENDC}: {normalized_occurrences}")

    save_data(name, results)


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
newspaper_articles = [(path.splitext(file_name)[0], spark.read.json(f"/data/{file_name}")) for file_name in DATA_FILES]

categorized_words = categorize_words(WORDS_TO_ANALYZE)

print(f"\n{Colors.BOLD}▶ Word occurrences:{Colors.ENDC}")

start = time()

# Analyze the newspapers (Spark Analysis).
for name, articles in newspaper_articles:
    analyze_newspaper(name, articles, categorized_words)

end = time()

print(f"\n{Colors.BOLD}▶ Execution time:{Colors.ENDC} {round(end - start, 3)}")