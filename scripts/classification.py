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


def get_data(newspaper_filename):
    newspapers = spark.read.json(f"hdfs:///data/{newspaper_filename}")
    return newspapers.withColumn("newspaper", lit(path.splitext(newspaper_filename)[0]))


def merge_articles(newspaper_filenames):
    return reduce(DataFrame.union, [get_data(newspaper_filename) for newspaper_filename in newspaper_filenames])


def train_model(data, number_of_partitions):
    data = data.repartition(number_of_partitions)  # Create n partitions.
    data = pipeline.fit(data).transform(data)  # Fit the pipeline to training documents.

    # Randomly split data into training and test sets, and set seed for reproducibility.
    (training_set, test_set) = data.randomSplit([0.7, 0.3], seed=100)

    # Train model with Training Data.
    model = logistic_regression.fit(training_set)

    # Return model and test set.
    return model, test_set


# Load the environment variables from .env file.
load_env_variables(".env")

# Get environment variables.
LEAVER_NEWSPAPER_FILES = getenv("LEAVER_NEWSPAPER_FILES").split(" ")
REMAIN_NEWSPAPER_FILES = getenv("REMAIN_NEWSPAPER_FILES").split(" ")
NEUTRAL_NEWSPAPER_FILE = getenv("NEUTRAL_NEWSPAPER_FILE").split(" ")

# Define Spark context.
spark = SparkSession.builder.appName("Classification").getOrCreate()
sc = spark.sparkContext

# Set Spark log level to error (it will show only error messages).
sc.setLogLevel("ERROR")

# Set a regular expression tokenizer.
regex_tokenizer = RegexTokenizer(inputCol="content", outputCol="tokens", pattern="\\W")

# Add HashingTF and IDF to transformation.
hashing_TF = HashingTF(inputCol="tokens", outputCol="rawFeatures", numFeatures=10000)
idf = IDF(inputCol="rawFeatures", outputCol="features", minDocFreq=5)

# Define a pipeline with all stages.
pipeline = Pipeline(stages=[regex_tokenizer, hashing_TF, idf])

# Create a logistic regression object.
logistic_regression = LogisticRegression(maxIter=20, regParam=0.3, elasticNetParam=0, family="binomial")

# Create an object to save all the results.
results = {}

start = time()

# [1]: Train a model using main Brexit articles (all Brexit newspapers without last one for each political part)
# to check when an article is for Brexit or not.

# Merge main Brexit newspaper articles.
articles = reduce(DataFrame.union, [
    merge_articles(LEAVER_NEWSPAPER_FILES[:-1]).withColumn("label", lit(0)),
    merge_articles(REMAIN_NEWSPAPER_FILES[:-1]).withColumn("label", lit(1))
])

# Train a model.
model, test_set = train_model(articles, len(LEAVER_NEWSPAPER_FILES + REMAIN_NEWSPAPER_FILES) - 2)

# Add training and test set accuracies to results.
results["leave/remain"] = {
    "training_set": model.summary.accuracy,
    "test_set": model.evaluate(test_set).accuracy
}

# [2]: Test created model with last newspapers not used in the previous dataset.

# Merge additional brexit newspaper articles.
additional_articles = reduce(DataFrame.union, [
    get_data(LEAVER_NEWSPAPER_FILES[-1]).withColumn("label", lit(0)),
    get_data(REMAIN_NEWSPAPER_FILES[-1]).withColumn("label", lit(1))
])

# Create n partitions and fit the pipeline to training documents.
additional_articles = additional_articles.repartition(2)
additional_articles = pipeline.fit(additional_articles).transform(additional_articles)

# Add accuracy to results.
results["leave/remain"]["additional_test_set"] = model.evaluate(additional_articles).accuracy

# [3]: Train another model using main Brexit and neutral articles to check when an articles talks about Brexit or not.

# Merge main Brexit and neutral newspaper articles.
articles = reduce(DataFrame.union, [
    merge_articles(NEUTRAL_NEWSPAPER_FILE).withColumn("label", lit(0)),
    merge_articles(LEAVER_NEWSPAPER_FILES[:-1] + REMAIN_NEWSPAPER_FILES[:-1]).withColumn("label", lit(1))
])

# Train a model.
model, test_set = train_model(articles, len(LEAVER_NEWSPAPER_FILES + REMAIN_NEWSPAPER_FILES) - 1)

# Add accuracies to results.
results["brexit/neutral"] = {
    "training_set": model.summary.accuracy,
    "test_set": model.evaluate(test_set).accuracy
}

end = time()

save_data("classification_results", results)

print(f"\n▶ Execution completed successfully in \033[1m{round(end - start, 3)}\033[0m seconds!")
