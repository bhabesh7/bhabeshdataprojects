import tweepy
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
import matplotlib.pyplot as plt
from tweepy import Cursor, API
import json
import Constant

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
        # bhabeshtweetapp at developer.twitter.com
        # app name -> bhabesh83app
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