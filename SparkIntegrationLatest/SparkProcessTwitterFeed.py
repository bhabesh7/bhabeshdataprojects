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

    lines = spark.readStream.format("socket").option("host", host).option("port", port).load()

    words = lines.select(explode(split(lines.value, " ")).alias("word"))

    def extract_tags(word):
        if word.lower().startswith("#"):
            return word
        else:
            return "nonTag"

    extract_tag_udf = udf(extract_tags, StringType())
    resultDF = words.withColumn("tags", extract_tag_udf(words.word))
    hashtagsDF = resultDF.withColumn("timestamp", current_timestamp())
    #hashtagCounts = resultDF.where(resultDF.tags != "nonTag").groupBy("tags").count().orderBy("count", ascending=False)
    #hashtagCounts = hashtagsDF.where(hashtagsDF.tags != "nonTag").groupBy("tags").count().orderBy("count", ascending=False)

    windowedCounts = hashtagsDF.withWatermark("timestamp", "500 milliseconds").\
        groupBy(window("timestamp", "10 seconds")).\
        count()

    windowedCounts.show()
    #getting error in spark submit for the writeStream line-- need to fix
    query = windowedCounts.\
       writeStream.\
       outputMode('complete').\
       format('console').\
        option('truncate', 'false').\
        start().awaitTermination()


    # query = windowedCounts. \
    #     writeStream. \
    #     format('csv'). \
    #     option('checkpointLocation', 'checkpoint/'). \
    #     start("output/").\
    #     awaitTermination()