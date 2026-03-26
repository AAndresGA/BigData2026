from pyspark.sql import SparkSession


def main() -> None:
    spark = SparkSession.builder.appName("wordcount").getOrCreate()
    data = [("big data con docker",), ("spark dask airflow",)]
    df = spark.createDataFrame(data, ["line"])

    words = (
        df.selectExpr("explode(split(line, ' ')) as word")
        .groupBy("word")
        .count()
        .orderBy("count", ascending=False)
    )
    words.show(truncate=False)
    spark.stop()


if __name__ == "__main__":
    main()
