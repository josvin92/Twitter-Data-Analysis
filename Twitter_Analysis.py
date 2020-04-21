# -*- coding: utf-8 -*-
"""
Created on Sun Apr 12 12:37:27 2020

@author: JOSVIN THOMAS JOHN
"""

import re
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob
import json
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import seaborn as sns
import nltk

class TwitterClient(object):
    '''
	Generic Twitter Class for sentiment analysis. 
	'''

    def __init__(self):
        '''
		Class constructor or initialization method. 
		'''
        # keys and tokens from the Twitter Dev Console
        consumer_key = 'XXXXXX'
        consumer_secret = 'XXXXXX'
        access_token = 'XXXXXX'
        access_token_secret = 'XXXXXX'

        # attempt authentication
        try:
            # create OAuthHandler object
            self.auth = OAuthHandler(consumer_key, consumer_secret)
            # set access token and secret
            self.auth.set_access_token(access_token, access_token_secret)
            # create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth)
        except:
            print("Error: Authentication Failed")

    def clean_tweet(self, tweet):
        '''
		Utility function to clean tweet text by removing links, special characters 
		using simple regex statements. 
		'''
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def get_tweet_sentiment(self, tweet):
        '''
		Utility function to classify sentiment of passed tweet 
		using textblob's sentiment method 
		'''
        # create TextBlob object of passed tweet text
        analysis = TextBlob(self.clean_tweet(tweet))
        polarity = analysis.sentiment.polarity
        # set sentiment
        if analysis.sentiment.polarity > 0:
            sentiment1 = 'positive'
        elif analysis.sentiment.polarity == 0:
            sentiment1 = 'neutral'
        else:
            sentiment1 = 'negative'
        return sentiment1, polarity

    def get_tweets(self, query, count=10):
        '''
		Main function to fetch tweets and parse them. 
		'''
        # empty list to store parsed tweets
        tweets = []
        try:
            # call twitter api to fetch tweets written in English
            # Append filter to query string to exclude retweets
            # query += ' -filter:retweets'
            # fetched_tweets = self.api.search(q=query, count=count, lang='en')
            fetched_tweets = tweepy.Cursor(self.api.search, q='\"{}\" -filter:retweets'.format(query), count=count,
                                           lang='en', tweet_mode='extended').items()
            counter = 0  # counter to keep track of each iteration

            # parsing tweets one by one
            for tweet in fetched_tweets:
                # empty dictionary to store required params of a tweet
                tweet_details = {}
                # Checking if retweets have been removed to get more meaningful information
                if (not tweet.retweeted) and ('RT @' not in tweet.full_text):

                    tweet_details['id'] = tweet.id
                    tweet_details['len'] = len(tweet.full_text)
                    tweet_details['name'] = tweet.user.screen_name
                    tweet_details['tweet'] = self.clean_tweet(tweet.full_text)
                    tweet_details['retweets'] = tweet.retweet_count
                    tweet_details['location'] = tweet.user.location
                    tweet_details['created'] = tweet.created_at.strftime('%Y-%m-%d %H:%M:%S')
                    tweet_details['followers'] = tweet.user.followers_count
                    tweet_details['likes'] = tweet.favorite_count
                    tweet_details['source'] = tweet.source
                    tweet_details['hashtag'] = hashtag_extract(tweet.full_text)
                    tweet_details['is_user_verified'] = tweet.user.verified
                    tweet_details['sentiment'], tweet_details['polarity'] = self.get_tweet_sentiment(tweet.full_text)

                    tweets.append(tweet_details)
                    counter += 1
                    if counter == count:
                        break
                    else:
                        pass

            # create directory 'data' if it does not exist
            if not (os.path.exists(os.getcwd() + os.sep + 'data')):
                os.mkdir("./data")
            # write tweets data to json file
            with open('data/{}.json'.format(query), 'w') as f:
                json.dump(tweets, f, indent=4, sort_keys=True)
            # return parsed tweets
            return tweets

        except tweepy.TweepError as e:
            # print error (if any)
            print("Error : " + str(e))
            print("Try again after 15 mins")


def hashtag_extract(text):
    # hashtags = re.findall(r"#(\w+)", s)
    lst = re.findall(r'\B#\w*[a-zA-Z]+\w*', text)
    lst = [e[1:] for e in lst]
    # return hashtags
    return lst

def sourceanalysis(tweets, name):
    tweets['source2'] = ''
    pd.set_option('mode.chained_assignment', None)

    for i in range(len(tweets['source'])):
        if tweets['source'][i] not in ['Twitter for Android', 'Instagram', 'Twitter Web Client', 'Twitter Web App', 'Twitter for iPhone', 'Twitter for iPad']:
            tweets['source2'][i] = 'Others'
        else:
            tweets['source2'][i] = tweets['source'][i]

    tweets_by_type2 = tweets.groupby(['source2'])['followers'].sum().sort_values()
    tweets_by_type2.rename("", inplace=True)

    size = int(len(tweets_by_type2) / 2)
    small = tweets_by_type2[:size]
    large = tweets_by_type2[size:]

    reordered = pd.concat([large[::2], small[::2], large[1::2], small[1::2]])
    angle = 180 + float(sum(small[::2])) / sum(reordered) * 360

    reordered.transpose().plot(kind='pie', figsize=(20, 15), autopct='%1.1f%%', shadow=False, explode=None, startangle=angle, labeldistance=1.05)
    plt.legend(bbox_to_anchor=(1, 1), loc=6, borderaxespad=0.)
    plt.title('Number of followers by Source - ' + name, bbox={'facecolor': '0.8', 'pad': 5})
    plt.show()


def sentiment(tweets, name):
    print("\n########################################################################")
    print("Start New Set of Tweets")
    # print length of tweets
    print("\nNumber of {} tweets = {}".format(name, len(tweets)))
    # picking positive tweets from tweets
    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
    # percentage of positive tweets
    positivepercent = 100 * len(ptweets) / len(tweets)
    print("Positive {} tweets percentage: {} %".format(name, positivepercent))
    # picking negative tweets from tweets
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
    # percentage of negative tweets
    negativepercent = 100 * len(ntweets) / len(tweets)
    print("Negative {} tweets percentage: {} %".format(name, negativepercent))
    # picking neutral tweets from tweets
    neutral = [tweet for tweet in tweets if tweet['sentiment'] == 'neutral']
    # percentage of neutral tweets
    neutralpercent = 100 * len(neutral) / len(tweets)
    print("Neutral {} tweets percentage: {} %".format(name, neutralpercent))
    # printing first 5 positive tweets
    print("\n\nPositive {} tweets:".format(name))
    for tweet in ptweets[:5]:
        print(tweet['tweet'])

    # printing first 5 negative tweets
    print("\n\nNegative {} tweets:".format(name))
    for tweet in ntweets[:5]:
        print(tweet['tweet'])

    return positivepercent

def freqdist_words(tweets, name):
    # extracting hashtags from non racist/sexist tweets
    HT_positive = [tweet['hashtag'] for tweet in tweets if tweet['sentiment'] == 'positive']
    # extracting hashtags from racist/sexist tweets
    HT_negative = [tweet['hashtag'] for tweet in tweets if tweet['sentiment'] == 'negative']

    # unnesting list
    HT_positive = sum(HT_positive, [])
    HT_negative = sum(HT_negative, [])
    # print(HT_positive)
    # print(HT_negative)

    if HT_positive:
        a = nltk.FreqDist(HT_positive)
        # print(a.keys())
        # print(a.values())
        d = pd.DataFrame({'Hashtag': list(a.keys()),
                          'Count': list(a.values())})
        # selecting top 10 most frequent hashtags
        d = d.nlargest(columns="Count", n=10)
        plt.figure(figsize=(16, 5))
        ax = sns.barplot(data=d, x="Hashtag", y="Count")
        ax.set_title("Top 10 most frequent hashtags from positive tweets - " + name, fontsize=15)
        # Set the x-axis label
        ax.set_xlabel("Hashtags")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right")
        # Set the y-axis label
        ax.set_ylabel("Count")
        plt.show()
    else:
        print("No Positive Hashtags to print")

    if HT_negative:
        a = nltk.FreqDist(HT_negative)
        # print(a.keys())
        # print(a.values())
        d = pd.DataFrame({'Hashtag': list(a.keys()),
                          'Count': list(a.values())})
        # selecting top 10 most frequent hashtags
        d = d.nlargest(columns="Count", n=10)
        plt.figure(figsize=(16, 5))
        ax = sns.barplot(data=d, x="Hashtag", y="Count")
        ax.set_title("Top 10 most frequent hashtags from negative tweets - " + name, fontsize=15)
        # Set the x-axis label
        ax.set_xlabel("Hashtags")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right")
        # Set the y-axis label
        ax.set_ylabel("Count")
        plt.show()
    else:
        print("No Negative Hashtags to print")


def data_analysis(tweets, name):
    # We create a pandas dataframe as follows:
    data = pd.DataFrame(data=[tweet['tweet'] for tweet in tweets], columns=['Tweets'])

    data['ID'] = [tweet['id'] for tweet in tweets]
    data['len'] = [tweet['len'] for tweet in tweets]
    data['Date'] = [datetime.datetime.strptime(tweet['created'], '%Y-%m-%d %H:%M:%S') for tweet in tweets]
    data['likes'] = [tweet['likes'] for tweet in tweets]
    data['RTs'] = [tweet['retweets'] for tweet in tweets]
    data['polarity'] = [tweet['polarity'] for tweet in tweets]
    data['source'] = [tweet['source'] for tweet in tweets]
    data['followers'] = [tweet['followers'] for tweet in tweets]
    # We display the first 10 elements of the dataframe:
    # print(data.head(5))

    # We extract the mean of lenghts:
    mean = np.mean(data['len'])
    print("\n\nThe average length of {} tweets: {}".format(name, mean))

    # We extract the tweet with more FAVs and more RTs:

    fav_max = np.max(data['likes'])
    rt_max = np.max(data['RTs'])

    fav = data[data.likes == fav_max].index[0]
    rt = data[data.RTs == rt_max].index[0]

    # Max FAVs:
    print("\nThe tweet with the most likes for {} is: \n{}".format(name, data['Tweets'][fav]))
    print("Number of likes: {}".format(fav_max))
    print("The number of characters of this tweet is {}.\n".format(data['len'][fav]))

    # Max RTs:
    print("\nThe tweet with the most retweets for {} is: \n{}".format(name, data['Tweets'][rt]))
    print("Number of retweets: {}".format(rt_max))
    print("The number of characters of this tweet is {}.\n".format(data['len'][rt]))

    tgroups = data.groupby('Date')['ID'].count()
    # print(tgroups.keys())
    # print(tgroups.values)
    # tgroups.to_excel('output.xlsx', header=True)

    # We create time series for data:
    numoftweets = pd.Series(data=tgroups.values, index=tgroups.keys())
    # Number of Tweets along time:
    ax = numoftweets.plot(figsize=(16, 4), color='r');
    ax.set_title("Number of Tweets over Time - " + name, fontsize=15)
    # Set the x-axis label
    ax.set_xlabel("Time")

    # Set the y-axis label
    ax.set_ylabel("Number of Tweets")
    plt.show()

    # t1 = data.groupby('Date')['polarity'].value_counts()
    tpolaritygroups = data.groupby('Date')['polarity'].mean()
    # print(tpolaritygroups.keys())
    # print(tpolaritygroups.values)
    # tpolaritygroups.to_excel('output.xlsx', header=True)

    # We create time series for data:
    polarity_scores = pd.Series(data=tpolaritygroups.values, index=tpolaritygroups.keys())
    # Number of Tweets along time:
    ax = polarity_scores.plot(figsize=(16, 4), color='r');
    ax.set_title("Sentiment Polarity Score over Time - " + name, fontsize=15)
    # Set the x-axis label
    ax.set_xlabel("Time")

    # Set the y-axis label
    ax.set_ylabel("Sentiment Polarity Score")
    plt.show()

    sourceanalysis(data, name)

    # tlen = pd.Series(data=data['len'].values, index=data['Date'])
    # numlikes = pd.Series(data=data['likes'].values, index=data['Date'])
    # numrts = pd.Series(data=data['RTs'].values, index=data['Date'])

    # Lenghts along time:
    # tlen.plot(figsize=(16, 4), color='r');
    # plt.show()

    # Likes vs retweets visualization:
    # numlikes.plot(figsize=(16, 4), label="Likes", legend=True)
    # numrts.plot(figsize=(16, 4), label="Retweets", legend=True);
    # plt.show()


def main():
    # creating object of TwitterClient Class
    api = TwitterClient()
    count = 2000
    # calling function to get tweets
    query1 = 'Donald Trump'
    trumptweets = api.get_tweets(query=query1, count=count)

    # print sentiment calculation of tweets
    positivepercent1 = sentiment(trumptweets, query1)

    # print data analysis of tweets
    data_analysis(trumptweets, query1)

    # print bar plot of famous hashtags
    freqdist_words(trumptweets, query1)

    # #############
    # #Biden Tweets
    # creating object of TwitterClient Class
    api2 = TwitterClient()
    # calling function to get tweets
    query2 = 'Joe Biden'
    bidentweets = api2.get_tweets(query=query2, count=count)

    # print sentiment calculation of tweets
    positivepercent2 = sentiment(bidentweets, query2)

    # print data analysis of tweets
    data_analysis(bidentweets, query2)

    # print bar plot of famous hashtags
    freqdist_words(bidentweets, query2)

    ####################################################################################
    # FINAL PREDICTION BASED ON WHICH CANDIDATE HAS MORE PERCENTAGE OF POSITIVE TWEETS
    ####################################################################################
    if positivepercent1 > positivepercent2:
        print("\nBased on the above analysis, {} will be elected in the 2020 presidential election".format(query1))
    elif positivepercent2 > positivepercent1:
        print("\nBased on the above analysis, {} will be elected in the 2020 presidential election".format(query2))
    else:
        print("\nBased on the above analysis, both {} and {} have equal chance of winning the 2020 presidential election".format(
                query1, query2))


if __name__ == "__main__":
    # calling main function
    main()
