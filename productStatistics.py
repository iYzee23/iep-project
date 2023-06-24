from pyspark.sql import SparkSession
from pyspark.sql.functions import sum, when, col
import os, json

DATABASE_IP = os.environ["DATABASE_URL"] if "DATABASE_URL" in os.environ else "localhost"

builder = SparkSession.builder.appName("PySpark Category Statistics")

builder = builder.config(
    "spark.driver.extraClassPath",
    "mysql-connector-j-8.0.33.jar"
)

spark = builder.getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

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

statistics = product_df.join(
    product_order_df,
    product_df["id"] == product_order_df["product_id"], "left"
).join(
    order_df,
    product_order_df["order_id"] == order_df["id"], "left"
).groupBy(
    product_df["name"]
).agg(
    sum(when(
        order_df["status"] == "COMPLETE",
        product_order_df["quantity"]
    ).otherwise(0)).alias("sold"),
    sum(when(
        (order_df["status"] == "CREATED") | (order_df["status"] == "PENDING"),
        product_order_df["quantity"]
    ).otherwise(0)).alias("waiting")
).filter(
    (col("sold") + col("waiting") > 0)
).orderBy(
    product_df["name"]
).collect()

result = {"statistics": []}
for row in statistics:
    result["statistics"].append({"name": row.name, "sold": int(row.sold), "waiting": int(row.waiting)})

with open("/app/resultProductStatistics.json", "w") as file:
    json.dump(result, file)

spark.stop()
