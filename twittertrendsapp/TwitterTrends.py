# Author: Bhabesh Acharya
# Date: 21-03-2020
#Libs: Tweepy, pandas, numpy, matplotlib, beautifulsoup4, textblob
# Credits to https://www.youtube.com/watch?v=rhBZqEWsZU4&t=967s and relatedvideos
# Purpose: Get tweets of user and perform sentiment and trend analysis
# python3 TwitterTrends.py <user>

import sys
import socket
import json
import pandas as pd
import numpy as np
from tweepy import Cursor, API
from bs4 import BeautifulSoup
import os
from textblob import TextBlob
import re
import Constant

# from contextlib import closing

import tweepy
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
import matplotlib.pyplot as plt
# import tkinter
# import matplotlib


#This is to enable UI mode for python
# matplotlib.use('TkAgg')

class TwitterClient:
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticate().authenticate()
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    # Cursor method in Tweepy api
    def get_user_timeline_tweets(self, num_tweets):
        tweetlist = []
        # sample
        # for tweet in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_tweets):
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweetlist.append(tweet)
        return tweetlist

    def get_followers_count(self):
        tuser = self.twitter_client.get_user(self.twitter_user)
        return tuser.followers_count

class TweetsListener(StreamListener):
    def __init__(self):
        print("Tweets listener initialized")
        # self.client_socket = socket

    def on_data(self, raw_data):
        try:
            jsonMsg = json.loads(raw_data)
            msg = jsonMsg["text"].encode("utf-8")
            print(dir(raw_data))
            print(msg)
            # self.client_socket.send(msg)
        except BaseException as e:
            print("error os data: %s" % str(e))
        return True

    def on_error(self, status_code):
        print(status_code)
        return True


class TwitterAuthenticate:
    def authenticate(self):       
        api_key = Constant.TWITTER_API_KEY
        api_secret = Constant.TWITTER_API_SECRET
        access_token = Constant.TWITTER_ACCESS_TOKEN
        access_token_secret = Constant.TWITTER_ACCESS_TOKEN_SECRET
        auth = OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_token_secret)
        return auth


class TwitterStreamer:
    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticate()
        pass

    def connect_to_twitter(self, tracks):
        twitter_auth = TwitterAuthenticate()
        auth = self.twitter_authenticator.authenticate()
        twitter_stream = Stream(auth, TweetsListener())
        twitter_stream.filter(track=tracks, languages=["en"])


class TweetAnalysis:
    def tweet_to_dataframe(self, tweets):
        dframe = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['tweets'])
        dframe['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        dframe['date'] = np.array([tweet.created_at for tweet in tweets])
        dframe['source'] = np.array([tweet.source for tweet in tweets])
        dframe['retweets'] = np.array([tweet.retweet_count for tweet in tweets])
        # dframe['retweets'] = pd.DataFrame(data=[tweet.retweet_count for tweet in tweets], columns=['likes'])
        return dframe

    def get_tweet_sentiment(self, tweet):
        sent = TextBlob(self.clean_tweet(tweet))
        polarity, subjectivity = sent.sentiment
        if polarity >0:
            return 1
        elif polarity == 0:
            return 0
        elif polarity <0:
            return -1

    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

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
    if len(tweets) or 0:
        print(dir(tweets[0]))
    tweet_analysis = TweetAnalysis()
    df = tweet_analysis.tweet_to_dataframe(tweets)
    df['sentiment'] = np.array([tweet_analysis.get_tweet_sentiment(tweet) for tweet in df['tweets']])

    print(df.head(5))

    print('max likes ', np.max(df['likes']))
    #time series plot (y axis,x axis)
    time_likes = pd.Series(df['likes'].values, index=df['date'])
    time_likes.plot(figsize=(16,4), label="likes", legend=True)

    time_retweets = pd.Series(df["retweets"].values, index = df['date'])
    time_retweets.plot(figsize=(16,4), label="retweets", legend=True)

    # will need tkinter fix for plt.show() to work fine
    # plt.show()
    basefilename = user + "_tweets"
    tempfile = basefilename + "_temp.html"
    plt.savefig(basefilename + ".png")

    #sort by likes in descending order
    df.sort_values(by=['likes', 'retweets'], inplace=True, ascending=False)
    dfhtml=df.to_html(tempfile)

    htmlDoc = open(tempfile).read()
    soup= BeautifulSoup(htmlDoc, features='html.parser')
    title="Latest "+ str(Constant.NUM_TWEETS) + " tweets of @" + user +" [Followers " + str(followers_count) + "]"

    title_tag = soup.new_tag('h1')
    title_tag.string = title
    img_tag = soup.new_tag('img', src=basefilename + ".png")
    soup.insert(0, title_tag)
    soup.insert(1, img_tag)

    html_new = soup.prettify('utf-8')

    with open(basefilename + ".html", "wb") as basefile:
        basefile.write(html_new)
    os.remove(tempfile)
    print("Twitter trend saved successfully ", basefilename)

    # old way
    # twitterFeed = TwitterStreamer()
    # twitterFeed.connect_to_twitter(tracks)
