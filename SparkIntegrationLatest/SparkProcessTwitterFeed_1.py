#Author: Bhabesh Acharya
#Date: 21-03-2020
#Purpose: listen to twitter feeds at local port and get count for every #tag
# python SparkProcessTwitter.py localhost 9998
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, udf, current_timestamp, window
from pyspark.sql.functions import split
from pyspark.sql.types import StringType


#
if __name__=="__main__":
    if len(sys.argv) !=3:
        print("usage spark-submit xyz.py <host> <port>",file=sys.stderr)
        exit(-1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    #try this option
    #sqlContext.sql("set spark.sql.shuffle.partitions=10")
    spark = SparkSession.builder.appName("SparkProcessTwitterFeed").getOrCreate()
    lines = spark.readStream.format("socket").option("host", host).option("port", port).load()

    #words = lines.as[String].flatMap(_.split(" "))
    #words =lines.rdd.flatMap(split(" "))
    # words = lines.select(explode(split(lines.value, " ")).alias("word"))
    words = lines.select(
        explode(
            split(lines.value, " ")
        ).alias("word")
    )
    wordCounts = words.groupBy("word").count()
    # words.withColumn("timestamp", current_timestamp())
    #wordCounts = words.groupBy("value").count()

    query = wordCounts.writeStream.\
        outputMode("complete").\
        format("console").\
        start()

    query.awaitTermination()
