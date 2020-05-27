# Author: Bhabesh Acharya
# Date: 21-03-2020
#Libs: Tweepy, pandas, numpy, matplotlib
# Credits to https://www.youtube.com/watch?v=rhBZqEWsZU4&t=967s and relatedvideos
# Purpose: Get Twitter feeds and stream it through a socket so that spark can process it.
# python3 TwitterTrends.py <user>

import sys
import socket
import json
import pandas as pd
import numpy as np
from tweepy import Cursor, API

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

    def get_user_timeline_tweets(self, num_tweets):
        tweetlist = []
        # sample
        # for tweet in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_tweets):
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweetlist.append(tweet)
        return tweetlist


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
        # bhabeshtweetapp at developer.twitter.com
        # app name -> bhabesh83app
        api_key = "Lef07eX2QRBAqq9sHPu66UBs7"
        api_secret = "wjnVXaUi8CMkypwlR23HwWobL7Ss9PaUVJODA55FFSXAVtrBme"
        access_token = "858757474240704512-TZzQuPXO3eR6keunVcbpZWu5d5NshUM"
        access_token_secret = "EJbnjpf7oQUC2avZgXJ8GdPWP5KqybW1iUqEwqY3SWbNN"
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


if __name__ == "__main__":
    if (len(sys.argv) < 2):
        print("invalid args provided. usage -> python3 TwitterFeed.py <user>", file=sys.stderr)
        exit(-1)
    user = sys.argv[1]
    # user = sys.argv[2]
    # tracks="covid19"
    # user="sachin_rt"
    print("user %s", user)
    client = TwitterClient(user)
    # tweetslist = client.get_user_timeline_tweets(10)
    # print(tweetslist)
    api = client.get_twitter_client_api()
    tweets = api.user_timeline(screen_name=user, count=10)
    print(dir(tweets[0]))
    tweet_analysis = TweetAnalysis()
    df = tweet_analysis.tweet_to_dataframe(tweets)
    print(df.head(5))

    print('max likes ', np.max(df['likes']))
    #time series plot (y axis,x axis)
    time_likes = pd.Series(df['likes'].values, index=df['date'])
    time_likes.plot(figsize=(16,4), label="likes", legend=True)

    time_retweets = pd.Series(df["retweets"].values, index = df['date'])
    time_retweets.plot(figsize=(16,4), label="retweets", legend=True)

    # will need tkinter fix for plt.show() to work fine
    # plt.show()
    file = user+"_tweets"
    plt.savefig(file+".png")

    #sort by likes in descending order
    df.sort_values(by=['likes', 'retweets'], inplace=True, ascending=False)
    df.to_html(file+".html")
    print("trend saved successfully ", file)
    # old way
    # twitterFeed = TwitterStreamer()
    # twitterFeed.connect_to_twitter(tracks)
