import json
from os import path, getenv
from time import time

from dotenv import load_dotenv
from pyspark.ml.feature import RegexTokenizer
from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, col


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

    print(f"\n{Colors.OKGREEN}Results saved in {file_name}.json file!{Colors.ENDC}")


def analyze_newspaper(name, articles):
    tokenized_articles = regex_tokenizer.transform(articles)

    words = tokenized_articles.select(explode('tokens').alias('words'))
    word_occurrences = words.groupBy('words').count().filter(col('words').isin(KEY_WORDS))

    number_of_words = words.count()

    print(f"\n#### {Colors.OKGREEN}{name}{Colors.ENDC}:")

    results = {
        "name": name,
        "words": {}
    }

    for word in word_occurrences.collect():
        normalized_occurrence = round(word["count"] / number_of_words * 1000, 3)

        results["words"][word["words"]] = normalized_occurrence

        print(f"* {Colors.OKBLUE}{word['words']}{Colors.ENDC}: {word['count']}, {normalized_occurrence}")

    return results


# Load the environment variables from .env file.
load_dotenv()

# Get environment variables.
ELASTIC_SEARCH_HOST = getenv("ELASTIC_SEARCH_HOST")
DATA_FILES = getenv("DATA_FILES").split(" ")
KEY_WORDS = getenv("KEY_WORDS").split(" ")

# Define Spark context.
spark = SparkSession.builder.master("local[*]").getOrCreate()
sc = spark.sparkContext

# Set Spark log level to error (it will show only error messages).
sc.setLogLevel("ERROR")

# Define the Spark tokenizer.
regex_tokenizer = RegexTokenizer(inputCol="content", outputCol="tokens", pattern="\\W")

# Get all newspaper's names.
newspaper_names = [path.splitext(file_name)[0] for file_name in DATA_FILES]

# Get all the articles of each newspaper.
newspaper_articles = [(path.splitext(file_name)[0], spark.read.json(f"/data/{file_name}")) for file_name in DATA_FILES]

print(f"\n{Colors.BOLD}▶ Word occurrences:{Colors.ENDC}")

start = time()

# Analyze the newspapers.
save_data("analysis_results", [analyze_newspaper(name, articles) for name, articles in newspaper_articles])

end = time()

print(f"\n{Colors.BOLD}▶ Execution time:{Colors.ENDC} {round(end - start, 3)}")
