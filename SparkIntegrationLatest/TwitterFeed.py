#Author: Bhabesh Acharya
#Date: 21-03-2020
#Purpose: Get Twitter feeds and stream it through a socket so that spark can process it.
# python TwitterFeed.py localhost 9998 "corona virus"

import sys
import socket
import json
from contextlib import closing

import tweepy

from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener

class TweetsListener(StreamListener):
    def __init__(self, socket):
        print("Tweets listener initialized")
        self.client_socket = socket

    def on_data(self, raw_data):
        try:
            jsonMsg = json.loads(raw_data)
            msg = jsonMsg["text"].encode("utf-8")
            print(msg)
            self.client_socket.send(msg)
        except BaseException as e:
            print("error os data: %s" % str(e))
        return True
    def on_error(self, status_code):
        print(status_code)
        return True

def connect_to_twitter(connection, tracks):
    #bhabeshtweetapp at developer.twitter.com
    #app name -> bhabesh83app
    api_key ="Lef07eX2QRBAqq9sHPu66UBs7"
    api_secret="wjnVXaUi8CMkypwlR23HwWobL7Ss9PaUVJODA55FFSXAVtrBme"
    access_token="858757474240704512-TZzQuPXO3eR6keunVcbpZWu5d5NshUM"
    access_token_secret="EJbnjpf7oQUC2avZgXJ8GdPWP5KqybW1iUqEwqY3SWbNN"
    auth =OAuthHandler(api_key, api_secret)
    auth.set_access_token(access_token,access_token_secret)
    twitter_stream = Stream(auth, TweetsListener(connection))
    twitter_stream.filter(track=tracks, languages=["en"])

def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #return s.getsockname()[1]
        return s

if __name__ == "__main__":
    if(len(sys.argv) < 4):
        print("invalid args provided. usage -> python TwitterFeed.py <hostname> <port> <tracks>", file=sys.stderr)
        exit(-1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    tracks = sys.argv[3]

    #s = find_free_port()
    #port = s.getsockname()[1]

    s = socket.socket()
    s.bind((host, port))
    print("listening on port %s"+ str(port))
    #listen(5) means only 5 concurrent connections will be entertained
    s.listen(5)
    connection, client = s.accept()
    print("connection request from %s"+ str(connection))
    print("tracks %s", tracks)

    connect_to_twitter(connection, tracks)


