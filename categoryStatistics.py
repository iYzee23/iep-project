from pyspark.sql import SparkSession
from pyspark.sql.functions import sum, when, col
import os, json

DATABASE_IP = os.environ["DATABASE_URL"] if "DATABASE_URL" in os.environ else "localhost"

builder = SparkSession.builder.appName("PySpark Product Statistics")

builder = builder.config(
    "spark.driver.extraClassPath",
    "mysql-connector-j-8.0.33.jar"
)

spark = builder.getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

category_df = spark.read.format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", f"jdbc:mysql://{DATABASE_IP}:3306/shop") \
    .option("dbtable", "category_table") \
    .option("user", "root") \
    .option("password", "root") \
    .load()

product_category_df = spark.read.format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", f"jdbc:mysql://{DATABASE_IP}:3306/shop") \
    .option("dbtable", "product_category_table") \
    .option("user", "root") \
    .option("password", "root") \
    .load()

product_df = spark.read.format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", f"jdbc:mysql://{DATABASE_IP}:3306/shop") \
    .option("dbtable", "product_table") \
    .option("user", "root") \
    .option("password", "root") \
    .load()

product_order_df = spark.read.format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", f"jdbc:mysql://{DATABASE_IP}:3306/shop") \
    .option("dbtable", "product_order_table") \
    .option("user", "root") \
    .option("password", "root") \
    .load()

order_df = spark.read.format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", f"jdbc:mysql://{DATABASE_IP}:3306/shop") \
    .option("dbtable", "order_table") \
    .option("user", "root") \
    .option("password", "root") \
    .load()

statistics = category_df.join(
    product_category_df,
    category_df["id"] == product_category_df["category_id"],
    "left"
).join(
    product_df,
    product_category_df["product_id"] == product_df["id"],
    "left"
).join(
    product_order_df,
    product_df["id"] == product_order_df["product_id"],
    "left"
).join(
    order_df,
    product_order_df["order_id"] == order_df["id"],
    "left"
).groupBy(
    category_df["name"]
).agg(
    sum(when(
        order_df["status"] == "COMPLETE",
        product_order_df["quantity"]
    ).otherwise(0)).alias("total_quantity")
).orderBy(
    col("total_quantity").desc(), category_df["name"]
).collect()

result = {"statistics": [row.name for row in statistics]}

with open("/app/resultCategoryStatistics.json", "w") as file:
    json.dump(result, file)

spark.stop()
