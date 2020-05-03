#Author: Bhabesh Acharya
#Date: 21-03-2020
#Purpose: listen to twitter feeds at local port and get count for every #tag
# python SparkProcessTwitter.py localhost 9998
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, udf, current_timestamp, window
from pyspark.sql.functions import split
from pyspark.sql.types import StringType


if __name__=="__main__":
    if len(sys.argv) !=3:
        print("usage spark-submit xyz.py <host> <port>",file=sys.stderr)
        exit(-1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    #try this option
    #sqlContext.sql("set spark.sql.shuffle.partitions=10")
    spark = SparkSession.builder.appName("SparkProcessTwitterFeed").getOrCreate()

    linesDF = spark.read.\
        option("inferSchema", "true").\
        option("header", "true").\
        csv("/home/bhabesh/PycharmProjects/SparkIntegrationLatest/data/uszips.csv")

    linesTDF =linesDF.withColumn("timestamp", current_timestamp())
    #partitionedDF =linesTDF.rdd.repartition(4)

    # filteredTDF  = linesTDF.filter(linesTDF("lat") > 18.40)


    linesTDF.write.\
        partitionBy("state_name").\
        option("header", "true").\
        mode("overwrite").\
        csv("/tmp/spark_output/zipcodes")


