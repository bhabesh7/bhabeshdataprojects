from bs4 import BeautifulSoup
import os
from os import path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import Constant
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

class GenerateReport:
    _resultsFolder = "results"
    _basefilename =None
    _tweet_df =None
    _tweet_ngrams_df =None
    _user =None
    _title =None
    _tempfile =None
    _ngrams_filename =None
    _wordcloud_filename =None
    _soup = None

    def __init__(self, user, title):
        self._user =user
        self._title =title
        if not path.exists(self._resultsFolder):
            os.mkdir(self._resultsFolder)

    def __get_text_from_dataframe(self):
        all_tweet_text = ' '
        for tweet in self._tweet_df["tweets"]:
            words_in_line = str(tweet).split(' ')
            for word in words_in_line:
                if word not in STOPWORDS:
                    all_tweet_text += str(tweet)
        return all_tweet_text

    def __write_wordcloud_png(self):
        all_tweet_text = self.__get_text_from_dataframe()
        stopwordsset = set(STOPWORDS)
        wordcloudIns = WordCloud(max_font_size=50, max_words=100, background_color="black",
                                 stopwords=stopwordsset, width=600, height=300).generate(all_tweet_text)
        # plt.figure()
        # plt.imshow(wordcloud, interpolation="bilinear")
        # plt.axis("off")
        savepath = path.join(self._resultsFolder, self._wordcloud_filename)
        WordCloud.to_file(self=wordcloudIns, filename=savepath)

    def __write_tweets_png(self):
        time_likes = pd.Series(self._tweet_df['likes'].values, index=self._tweet_df['date'])
        time_likes.plot(figsize=(16, 4), label="likes", legend=True)
        time_retweets = pd.Series(self._tweet_df["retweets"].values, index=self._tweet_df['date'])
        time_retweets.plot(figsize=(16, 4), label="retweets", legend=True)
        savepath = path.join(self._resultsFolder, self._basefilename + ".png")
        plt.savefig(savepath)
        #Clearing is needed for further plt.savefig to have independent plots
        time_likes = None
        time_retweets = None

    def __write_tweets_ngram_png(self):
        dframe_ngrams_top = self._tweet_ngrams_df.head(Constant.NUM_NGRAMS)
        dframe_ngrams_top.plot.bar(x='ngram', y='freq', rot=25)
        savepath = path.join(self._resultsFolder, self._ngrams_filename)
        plt.savefig(savepath)

    def __soup_add_img_with_caption(self, png_filename, caption):
        #add caption for the image
        caption_tag = self._soup.new_tag('h3')
        caption_tag.string = caption
        self._soup.append(caption_tag)
        #add link to the image
        img_tag = self._soup.new_tag('img', src=png_filename)
        self._soup.append(img_tag)

    def __write_tweets_html(self):
        self._tweet_df.sort_values(by=['likes', 'retweets'], inplace=True, ascending=False)
        dfhtml = self._tweet_df.to_html(self._tempfile)
        htmlDoc = open(self._tempfile).read()
        self._soup = BeautifulSoup(htmlDoc, features='html.parser')
        title = self._title
        title_tag = self._soup .new_tag('h1')
        title_tag.string = title
        self._soup.insert(0, title_tag)

        self.__soup_add_img_with_caption(png_filename=self._basefilename + ".png", caption="Tweet Trends")
        self.__soup_add_img_with_caption(png_filename=self._ngrams_filename, caption="Top N Grams")
        self.__soup_add_img_with_caption(png_filename=self._wordcloud_filename, caption="Tweet Wordcloud")
        html_new = self._soup.prettify('utf-16')

        savepath = path.join(self._resultsFolder, self._basefilename + ".html")
        with open(savepath, "wb") as basefile:
            basefile.write(html_new)

    def setupReport(self, tweet_df, tweet_ngrams_df):
        self._basefilename = self._user + "_tweets"
        self._tempfile = self._basefilename + "_temp.html"
        self._ngrams_filename = self._basefilename + "_ngrams.png"
        self._wordcloud_filename = self._basefilename + "_wordcloud.png"

        self._tweet_df =tweet_df
        self._tweet_ngrams_df = tweet_ngrams_df

        self.__write_tweets_png()
        self.__write_tweets_ngram_png()
        self.__write_wordcloud_png()
        self.__write_tweets_html()
        self.__cleanupReport()
        savepath = path.join(self._resultsFolder, self._basefilename+".html")
        print("Twitter trend saved successfully ", savepath)

    def __cleanupReport(self):
        os.remove(self._tempfile)
