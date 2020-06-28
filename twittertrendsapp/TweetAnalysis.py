import pandas as pd
import numpy as np
from textblob import TextBlob
import re


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
        if polarity > 0:
            return 1
        elif polarity == 0:
            return 0
        elif polarity < 0:
            return -1

    def get_ngrams_for_tweet(self, tweet, num):
        blob = TextBlob(self.clean_tweet(tweet))
        ngs = blob.ngrams(2)
        nglist = [' '.join(ng) for ng in ngs]
        return nglist

    def get_ngrams_counts_dict(self, global_tweet_ngramlist):
        dict = {}
        for g in global_tweet_ngramlist:
            if g not in dict:
                dict[g] = 1
            else:
                dict[g] += dict.get(g) + 1
        return dict
        # sortedbycount = {w: dict[w] for w in sorted(dict, key=dict.get, reverse=True)}
        # return list(sortedbycount.keys())[:N], list(sortedbycount.values())[:N]

    # gets the n-grams across tweets
    def get_ngram_global_list(self, ngrams_per_tweet_list):
        ngrams_global_list = []
        for ngramslist in ngrams_per_tweet_list:
            for ngram in ngramslist:
                ngrams_global_list.append(ngram)
        return ngrams_global_list

    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
