# Author: Bhabesh Acharya
# Date: 21-03-2020
# Libs: Tweepy, pandas, numpy, matplotlib, beautifulsoup4, textblob, wordcloud
# Credits to https://www.youtube.com/watch?v=rhBZqEWsZU4&t=967s and relatedvideos
# Purpose: Get tweets of user and perform sentiment and trend analysis
# python3 TwitterTrends.py <user>
# python -m textblob.download_corpora --. this downloads the corpus for text analytics like ngrams

import sys
import socket
import json
import pandas as pd
import numpy as np
import Constant
import GenerateHtml

# import tkinter
# import matplotlib

# nltk.download('punkt')
# This is to enable UI mode for python
# matplotlib.use('TkAgg')
from collections import Counter

from TweepyClasses import TwitterClient
from TweetAnalysis import TweetAnalysis


if __name__ == "__main__":
    if (len(sys.argv) < 2):
        print("invalid args provided. usage -> python3 TwitterFeed.py <user>", file=sys.stderr)
        exit(-1)
    user = sys.argv[1]
    # user = "sachin_rt"
    # tracks="covid19"
    # user="sachin_rt"
    print("user %s", user)
    client = TwitterClient(user)
    # tweetslist = client.get_user_timeline_tweets(10)
    # print(tweetslist)
    api = client.get_twitter_client_api()
    followers_count = client.get_followers_count()
    print("followers " + str(followers_count))
    tweets = api.user_timeline(screen_name=user, count=Constant.NUM_TWEETS)
    #shows the attributes of the json
    # if len(tweets) or 0:
    #     print(dir(tweets[0]))
    tweet_analysis = TweetAnalysis()
    df = tweet_analysis.tweet_to_dataframe(tweets)
    df['sentiment'] = np.array([tweet_analysis.get_tweet_sentiment(tweet) for tweet in df['tweets']])
    # n-grams for all the tweets
    ngrams_per_tweet_list = np.array([tweet_analysis.get_ngrams_for_tweet(tweet, 2) for tweet in df['tweets']])
    ngrams_global_list = tweet_analysis.get_ngram_global_list(ngrams_per_tweet_list)

    ngrams_dict = tweet_analysis.get_ngrams_counts_dict(ngrams_global_list)
    dframe_ngrams = pd.DataFrame(data=list(ngrams_dict.items()), columns=['ngram', 'freq'])
    dframe_ngrams.sort_values(by=['freq'], inplace=True, ascending=False)
    print(dframe_ngrams)
    print(df.head(5))

    print('max likes ', np.max(df['likes']))

    title = "Latest " + str(Constant.NUM_TWEETS) + " tweets of @" + user + " [Followers " + str(followers_count) + "]"
    genhtml = GenerateHtml.GenerateReport(user, title)
    genhtml.setupReport(tweet_df = df, tweet_ngrams_df= dframe_ngrams)
