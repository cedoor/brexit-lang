import ast
import json
from functools import reduce
from os import path, getenv, environ
from time import time

from pyspark.ml import Pipeline
from pyspark.ml.feature import RegexTokenizer, HashingTF, IDF
from pyspark.sql import SparkSession
from pyspark.sql.functions import DataFrame, lit


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

# Define Spark context.
spark = SparkSession.builder.appName("BrexitLang").getOrCreate()
sc = spark.sparkContext

# Set Spark log level to error (it will show only error messages).
sc.setLogLevel("ERROR")

# Merge all newspaper articles.
leaver_articles = merge_articles(LEAVER_NEWSPAPER_FILES).withColumn("label", 0)
remain_articles = merge_articles(REMAIN_NEWSPAPER_FILES).withColumn("label", 1)

# ...
brexit_articles = reduce(DataFrame.union, [leaver_articles, remain_articles])

# Create n partitions, where n is the number of newspapers to analyze.
brexit_articles = brexit_articles.repartition(len(LEAVER_NEWSPAPER_FILES) + len(REMAIN_NEWSPAPER_FILES))

# Regular expression tokenizer.
regex_tokenizer = RegexTokenizer(inputCol="content", outputCol="tokens", pattern="\\W")

# Add HashingTF and IDF to transformation.
hashing_TF = HashingTF(inputCol="tokens", outputCol="rawFeatures", numFeatures=10000)
idf = IDF(inputCol="rawFeatures", outputCol="features", minDocFreq=5)

print(f"\n{Colors.BOLD}▶ Cluster nodes: {sc._jsc.sc().getExecutorMemoryStatus().size()}")

start = time()

pipeline = Pipeline(stages=[regex_tokenizer, hashing_TF, idf])

# Fit the pipeline to training documents.
pipeline_fit = pipeline.fit(brexit_articles)
dataset = pipeline_fit.transform(brexit_articles)

# Randomly split data into training and test sets, and set seed for reproducibility.
(training_data, test_data) = dataset.randomSplit([0.7, 0.3], seed=100)

print(f"Training set articles: {str(training_data.count())}")
print(f"Test set articles: {str(test_data.count())}")

end = time()

# save_data("classification_results", results)

print(f"\n{Colors.BOLD}▶ Execution time:{Colors.ENDC} {round(end - start, 3)}")
