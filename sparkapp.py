from flask import Flask, jsonify
import subprocess, os, json

application = Flask(__name__)


@application.route("/sparkProducts", methods=["GET"])
def mSparkProducts():
    os.environ["SPARK_APPLICATION_PYTHON_LOCATION"] = "app/productStatistics.py"
    os.environ["SPARK_SUBMIT_ARGS"] = "--driver-class-path /app/mysql-connector-j-8.0.33.jar --jars /app/mysql-connector-j-8.0.33.jar"

    subprocess.check_output(["/template.sh"])
    with open("/app/resultProductStatistics.json", "r") as file:
        result = json.load(file)

    return jsonify(result)


@application.route("/sparkCategory", methods=["GET"])
def mSparkCategory():
    os.environ["SPARK_APPLICATION_PYTHON_LOCATION"] = "app/categoryStatistics.py"
    os.environ["SPARK_SUBMIT_ARGS"] = "--driver-class-path /app/mysql-connector-j-8.0.33.jar --jars /app/mysql-connector-j-8.0.33.jar"

    subprocess.check_output(["/template.sh"])
    with open("/app/resultCategoryStatistics.json", "r") as file:
        result = json.load(file)

    return jsonify(result)


if __name__ == "__main__":
    application.run(host="0.0.0.0")
