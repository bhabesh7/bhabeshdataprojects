#Author: Bhabesh Acharya
#Date: 29-03-2020
#Purpose: write csv files as multiple partitions and read those partitions
# spark-submit advancedpartitions.py
import sys
from pyspark.sql.functions import year, month, dayofmonth
from pyspark.sql import SparkSession
from datetime import date, timedelta
from pyspark.sql.types import IntegerType, DateType, StringType, StructType, StructField

appName = "PySpark Partition Example"
master = "local[8]"

# Create Spark session with Hive supported.
spark = SparkSession.builder \
    .appName(appName) \
    .master(master) \
    .getOrCreate()

print(spark.version)
# Populate sample data
start_date = date(2019, 1, 1)
data = []

for i in range(0,500):
    data.append({"Country": "CN", "Date": start_date + timedelta(days=i), "Amount": 10+i})
    data.append({"Country": "AU", "Date": start_date + timedelta(days=i), "Amount": 10*i})
    data.append({"Country": "IN", "Date": start_date + timedelta(days=i), "Amount": (10+i)+7*i})

schema = StructType([StructField("Country", StringType(), nullable=False),
                     StructField("Date", DateType(), nullable=False),
                     StructField("Amount", IntegerType(), nullable=False)])

df = spark.createDataFrame(data, schema=schema)
df.show()
print(df.rdd.getNumPartitions())
#df.write.mode("overwrite").csv("/tmp/spark_output/example.csv", header=True)

#create dataframe with year month day columns
dfcols =df.withColumn("Year", year("Date")).withColumn("Month", month("Date")).withColumn("Day", dayofmonth("Date"))
# write with multiple column partitions
dfpart = dfcols.repartition("Year", "Month", "Day", "Country")
# dfpart.write.mode("overwrite").csv("/tmp/spark_output/example.csv", header=True)
#write the partitions with files created with the year month day country patterns
dfpart.write.partitionBy("Year", "Month", "Day", "Country").mode("overwrite").csv("/tmp/spark_output/example.csv", header=True)

#https://kontext.tech/column/spark/296/data-partitioning-in-spark-pyspark-in-depth-walkthrough#comments

print("completed writing csv partitions")

#read partition
# df=spark.read.option("basePath","/tmp/spark_output/example.csv").csv("/tmp/spark_output/example.csv/Year=*/Month=1/Day=30")
