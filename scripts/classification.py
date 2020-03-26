import ast
import json
from functools import reduce
from os import path, getenv, environ
from time import time

from pyspark.ml import Pipeline
from pyspark.ml.classification import LogisticRegression
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


def get_data(newspaper_filename):
    newspapers = spark.read.json(f"hdfs:///data/{newspaper_filename}")
    return newspapers.withColumn("newspaper", lit(path.splitext(newspaper_filename)[0]))


def merge_articles(newspaper_filenames):
    return reduce(DataFrame.union, [get_data(newspaper_filename) for newspaper_filename in newspaper_filenames])


def train_model(data, number_of_partitions):
    # Create n partitions.
    data = data.repartition(number_of_partitions)

    # Fit the pipeline to training documents.
    data = pipeline.fit(data).transform(data)

    # Randomly split data into training and test sets, and set seed for reproducibility.
    (training_data, test_data) = data.randomSplit([0.7, 0.3], seed=100)

    # Train model with Training Data.
    model = logistic_regression.fit(training_data)

    # Return model and test set.
    return model, test_data


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

# Regular expression tokenizer.
regex_tokenizer = RegexTokenizer(inputCol="content", outputCol="tokens", pattern="\\W")

# Add HashingTF and IDF to transformation.
hashing_TF = HashingTF(inputCol="tokens", outputCol="rawFeatures", numFeatures=10000)
idf = IDF(inputCol="rawFeatures", outputCol="features", minDocFreq=5)

pipeline = Pipeline(stages=[regex_tokenizer, hashing_TF, idf])

# Build the model.
logistic_regression = LogisticRegression(maxIter=20, regParam=0.3, elasticNetParam=0, family="binomial")

results = {}

print(f"\n{Colors.BOLD}▶ Cluster nodes: {sc._jsc.sc().getExecutorMemoryStatus().size()}")

start = time()

# [1]: Training a model using main Brexit articles (all Brexit articles without last one for each political part).

# Merge main Brexit newspaper articles.
brexit_articles = reduce(DataFrame.union, [
    merge_articles(LEAVER_NEWSPAPER_FILES[:-1]).withColumn("label", 0),
    merge_articles(REMAIN_NEWSPAPER_FILES[:-1]).withColumn("label", 1)
])

# Train models and get accuracies.
brexit_model, brexit_test_data = train_model(brexit_articles, len(LEAVER_NEWSPAPER_FILES + REMAIN_NEWSPAPER_FILES) - 2)

# Add accuracies to results.
results["brexit"] = {
    "training_set": brexit_model.summary.accuracy,
    "test_set": brexit_model.evaluate(brexit_test_data).accuracy
}

# [2]: ...

# Merge additional brexit newspaper articles.
additional_brexit_articles = reduce(DataFrame.union, [
    get_data(LEAVER_NEWSPAPER_FILES[-1]).withColumn("label", 0),
    get_data(REMAIN_NEWSPAPER_FILES[-1]).withColumn("label", 1)
])

# Add accuracy to results.
results["brexit"]["additional_test_set"] = brexit_model.evaluate(additional_brexit_articles).accuracy

# [3]: ...

# ...
all_articles = reduce(DataFrame.union, [
    merge_articles(NEUTRAL_NEWSPAPER_FILE).withColumn("label", 0),
    merge_articles(LEAVER_NEWSPAPER_FILES[:-1] + REMAIN_NEWSPAPER_FILES[:-1]).withColumn("label", 1)
])

# Train models and get accuracies.
brexit_model, brexit_test_data = train_model(all_articles, len(LEAVER_NEWSPAPER_FILES + REMAIN_NEWSPAPER_FILES) - 1)

# Add accuracies to results.
results["neutral"] = {
    "training_set": brexit_model.summary.accuracy,
    "test_set": brexit_model.evaluate(brexit_test_data).accuracy
}

end = time()

save_data("classification_results", results)

print(f"\n{Colors.BOLD}▶ Execution time:{Colors.ENDC} {round(end - start, 3)}")
