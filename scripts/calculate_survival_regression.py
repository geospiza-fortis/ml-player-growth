import pickle
import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import pyspark
from lifelines import CoxPHFitter
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from tqdm.contrib.concurrent import thread_map


def transform(df):
    z = df.drop(columns=["name", "job", "max_level"]).copy()
    z = z[~z.isnull().any(axis=1)]
    cols = [c for c in z.columns if c.startswith("ttl") or c == "age"]
    for col in cols:
        z[col] = np.log(z[col])
    # filter out any fields with null values in them
    return z[~z.isnull().any(axis=1)]


def train_model(spark, level, field="exp_per_time"):
    """Use the last 10 levels and age as features, including up to 1 levels
    of characters to train the survival model."""

    diff = """
        (unix_timestamp(from_utc_timestamp("2021-08-01", "Z")) 
        - unix_timestamp(from_utc_timestamp(last_ts, "Z")))
    """
    exp = spark.sql("select * from exptable").collect()
    d = {row.level: row.exp for row in exp}
    pivot_expr = ",".join(
        [
            f"""
                min(if(level=={i}, {field}, null)) 
                as ttl_{i}
            """
            for i in range(3, level)
            if i >= level - 10
        ]
    )

    df = spark.sql(
        f"""
        with pivoted as (
            select
                name,
                job,
                max(level) as max_level,
                min(if(level={level} and time is not null, time, {diff})) as duration,
                max(if(level={level}, 1, 0)) as observed,
                {pivot_expr}
            from ttl
            group by name, job
        )
        select * from pivoted
        where
            duration >=0
            and max_level >= {level-1}
        """
    )
    pdf = df.toPandas()

    cph = CoxPHFitter().fit(
        transform(pdf), duration_col="duration", event_col="observed"
    )
    return cph


def main():
    os.environ["SPARK_HOME"] = pyspark.__path__[0]
    os.environ["PYSPARK_DRIVER_PYTHON"] = "python"
    os.environ["PYSPARK_PYTHON"] = "python"

    spark = SparkSession.builder.config("spark.driver.memory", "8g").getOrCreate()

    data = Path(__file__).parent.parent / "data"

    levels = spark.read.csv(
        f"{data}/20210801_all_levels.csv", header=True, inferSchema=True
    ).cache()
    levels.createOrReplaceTempView("levels")

    ranking = spark.read.csv(
        f"{data}/20210801_all_ranking.csv", header=True, inferSchema=True
    ).cache()
    ranking.createOrReplaceTempView("ranking")

    exptable = spark.read.csv(
        f"{data}/exptable.csv", header=True, inferSchema=True
    ).cache()
    exptable.createOrReplaceTempView("exptable")

    ttl = spark.sql(
        """
        with jobs as (
            select name, job
            from ranking
        )
        select
            name,
            job,
            level,
            lag(timestamp) over (partition by name order by level) as last_ts,
            unix_timestamp(from_utc_timestamp(timestamp, "Z"))
                - unix_timestamp(from_utc_timestamp(lag(timestamp) over (partition by name order by level), "Z"))
                as time,
            exp/(unix_timestamp(from_utc_timestamp(timestamp, "Z"))
                - unix_timestamp(from_utc_timestamp(lag(timestamp) over (partition by name order by level), "Z")))
                as exp_per_time
        from levels
        join jobs
        using (name)
        join exptable
        using (level)
        """
    ).cache()
    ttl.createOrReplaceTempView("ttl")

    output = data / "survival" / "cox_v2"
    output.mkdir(parents=True, exist_ok=True)

    def _train_save(level):
        model = train_model(spark, level)
        model_path = output / f"level_{level}.pickle"
        with model_path.open("wb") as fp:
            pickle.dump(model, fp)

    thread_map(_train_save, range(5, 201), max_workers=8)


if __name__ == "__main__":
    main()
