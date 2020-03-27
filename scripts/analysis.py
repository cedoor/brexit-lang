import ast
import json
from functools import reduce
from os import path, getenv, environ
from time import time

from pyspark.ml.feature import RegexTokenizer
from pyspark.sql import SparkSession
from pyspark.sql.functions import DataFrame, lit, explode, col, count, collect_list


# Define some console colors.
class Colors:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def load_env_variables(filepath):
    for key, value in get_env_line(filepath):
        environ.setdefault(key, str(value))


def get_env_line(filepath):
    for line in open(filepath):
        line = line.strip()

        if line.startswith('#') or '=' not in line:
            continue

        key, value = line.split('=', 1)
        key = key.strip().upper()
        value = value.strip()

        if not (key and value):
            continue

        try:
            value = ast.literal_eval(value)
        except (ValueError, SyntaxError):
            pass

        yield key, value


def save_data(file_name, data):
    with open("./" + file_name + ".json", "w") as fp:
        json.dump(data, fp, indent=4, ensure_ascii=False)

    print(f"\n{Colors.OKGREEN}Results saved in {file_name}.json file!{Colors.ENDC}")


def merge_articles(newspaper_filenames):
    dataframes = []

    for newspaper_filename in newspaper_filenames:
        newspapers = spark.read.json(f"hdfs:///data/{newspaper_filename}")
        dataframe = newspapers.withColumn("newspaper", lit(path.splitext(newspaper_filename)[0]))

        dataframes.append(dataframe)

    return reduce(DataFrame.union, dataframes)


# Load the environment variables from .env file.
load_env_variables(".env")

# Get environment variables.
LEAVER_NEWSPAPER_FILES = getenv("LEAVER_NEWSPAPER_FILES").split(" ")
REMAIN_NEWSPAPER_FILES = getenv("REMAIN_NEWSPAPER_FILES").split(" ")
NEUTRAL_NEWSPAPER_FILE = getenv("NEUTRAL_NEWSPAPER_FILE").split(" ")
DATA_FILES = LEAVER_NEWSPAPER_FILES + REMAIN_NEWSPAPER_FILES + NEUTRAL_NEWSPAPER_FILE
KEY_TOKENS = getenv("KEY_TOKENS").split(" ")

# Define Spark context.
spark = SparkSession.builder.appName("Analysis").getOrCreate()
sc = spark.sparkContext

# Set Spark log level to error (it will show only error messages).
sc.setLogLevel("ERROR")

# Merge all newspaper articles.
all_articles = merge_articles(DATA_FILES)

# Create n partitions, where n is the number of newspapers to analyze.
all_articles = all_articles.repartition(len(DATA_FILES))

# Define the Spark tokenizer.
regex_tokenizer = RegexTokenizer(inputCol="content", outputCol="tokens", pattern="\\W")

start = time()

# Tokenize all articles.
tokenized_articles = regex_tokenizer.transform(all_articles)
# Expand all tokens.
all_tokens = tokenized_articles.select(explode('tokens').alias('token'), 'newspaper')
# Count token occurrences for each newspaper.
token_occurrences = all_tokens.groupBy('token', 'newspaper').agg(count("*").alias("token_occurrence"))
# Filter tokens using to find only key words.
filtered_token_occurrences = token_occurrences.filter(col('token').isin(KEY_TOKENS))
# Group by newspapers.
newspapers = filtered_token_occurrences.groupBy('newspaper').agg(
    collect_list('token').alias("tokens"),
    collect_list('token_occurrence').alias("token_occurrences")
)
# Add total number of tokens for each newspaper.
newspapers = all_tokens.groupBy('newspaper').count().join(newspapers, "newspaper")
# Save all results in a structured object.
results = [{
    "name": newspaper["newspaper"],
    "total_tokens": newspaper["count"],
    "tokens": {
        token: round(newspaper["token_occurrences"][i] / newspaper["count"] * 1000, 3)
        for i, token in enumerate(newspaper["tokens"])
    }
} for newspaper in newspapers.collect()]

end = time()

save_data("analysis_results", results)

print(f"\n{Colors.BOLD}▶ Execution time:{Colors.ENDC} {round(end - start, 3)}")
