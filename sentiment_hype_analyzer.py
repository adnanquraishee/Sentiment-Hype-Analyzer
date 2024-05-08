# -*- coding: utf-8 -*-
"""Sentiment Hype Analyzer.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1e1JqFBk8lehge14VBFc2qkMtQKZFcADI
"""

pip install git+https://github.com/tweepy/tweepy.git

from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from textblob import TextBlob
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re

pip install -U textblob

"""Client for twitter"""

class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)

        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list

    def get_home_timeline_tweets(self, num_tweets):
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets

"""Twitter Authenticator"""

class TwitterAuthenticator():

    def authenticate_twitter_app(self):
        auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        return auth

"""Streamer for Tweets"""

class TwitterStreamer():
    """
    Class for streaming and processing live tweets.
    """
    def __init__(self):
        self.twitter_autenticator = TwitterAuthenticator()

    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        # This handles Twitter authetification and the connection to Twitter Streaming API
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_autenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)

        # This line filter Twitter Streams to capture data by the keywords:
        stream.filter(track=hash_tag_list)

"""Streamer For Listener"""

class TwitterListener(StreamListener):
    """
    This is a basic listener that just prints received tweets to stdout.
    """
    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self, data):
        try:
            print(data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(data)
            return True
        except BaseException as e:
            print("Error on_data %s" % str(e))
        return True

    def on_error(self, status):
        if status == 420:
            # Returning False on_data method in case rate limit occurs.
            return False
        print(status)

"""Analysis of Tweets"""

class TweetAnalyzer():
    """
    Functionality for analyzing and categorizing content from tweets.
    """

    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def analyze_sentiment(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))

        if analysis.sentiment.polarity > 0:
            return 1
        elif analysis.sentiment.polarity == 0:
            return 0
        else:
            return -1

    def tweets_to_data_frame(self, tweets):
        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['tweets'])

        df['id'] = np.array([tweet.id for tweet in tweets])
        df['len'] = np.array([len(tweet.text) for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['source'] = np.array([tweet.source for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])

        return df

pd.set_option('display.max_columns',1000)
pd.set_option('display.max_colwidth',100)
pd.set_option('display.max_rows',100)
pd.set_option('display.width',None)

"""Program For Application"""

if __name__ == '__main__':

    hype=0
    phype=0
    senti=0
    psenti=0
    x=int(input('Enter no. of tweets you want: '))
    analysis_client=input('Enter proper twitter handle: ')
    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()

    api = twitter_client.get_twitter_client_api()

    tweets = api.user_timeline(screen_name=analysis_client, count=200)

    df = tweet_analyzer.tweets_to_data_frame(tweets)
    df['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['tweets']])

    print(df.head(x))
    for i in range(0,x-1):
      hype= (df['retweets'][i]*0.5) + (df['likes'][i]*0.2) + hype
      senti= df['sentiment'][i] + senti
    hype=hype/x
    print("Hype of person in last ",x," Tweets is : ",hype)
    for i in range(x,(2*x)-1):
      phype= (df['retweets'][i]*0.5) + (df['likes'][i]*0.2) + phype
      psenti= df['sentiment'][i] + psenti
    phype=phype/x
    print("Hype of person in Previous ",x," than current Tweets is : ",phype)
    print("Hype Previous: ",phype," vs ",hype," : Current Hype")
    print("Sentiment Previous: ",psenti," vs ",senti," : Current Sentiment")
    if senti > psenti and hype > phype:
      print("Hype increased with increase in Positivity of tweets")
    elif senti > psenti and phype > hype:
      print("Hype decreased with increase in Positivity of tweets")
    elif psenti > senti and hype > phype:
      print("Hype increased with decrease in Positivity of tweets")
    elif psenti > senti and phype > hype:
      print("Hype decreased with decrease in Positivity of tweets")
    else:
      print("Hype remained same with same positivity of tweets as previous")