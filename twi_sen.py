#description : machine learning project for sentomental analysis using twitter feeds and tweepy
from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener #for data and status input
from tweepy import OAuthHandler #for authentication
from tweepy import Stream #for streaming data

from textblob import TextBlob

import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
import re
import login


####TWITTER CLIENT####
class TwitterClient():
    def __init__(self, twitter_user = None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user
        
    def get_twitter_client_api(self):
        return self.twitter_client
        
    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id = self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets
    
    def get_friend_list(self, num_friends):
        friend_list = []
        for friends in Cursor(self.twitter_client.friends, id = self.twitter_user).items(num_friends):
            friend_list.append(friends)
        return friend_list

    def get_home_timeline_tweets(self, num_tweets):
        pass

        
####TWITTER AUTHENTICATION####
class TwitterAuthenticator():
    def authenticate_twitter_app(self):
        auth = OAuthHandler(login.CONSUMER_KEY,login.CONSUMER_SECRET) #authentication for twitter
        auth.set_access_token(login.ACCESS_TOKEN,login.ACCESS_TOKEN_SECRET)
        return auth


####TWITTER STREAMER CLASS####
class TwitterStreamer():
    """
    class for streaming and processing live tweets
    """
    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()
        
    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        #this handle the twitter authentication and connection to twitter streaming API 
        listener = TwitterListener(fetched_tweets_filename) #object to bring the data and any error caused
        auth = self.twitter_authenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)
        
        #stream.filter(track = ['donald trump','narendra modi','amit shah','rahul gandhi'])
        stream.filter(track = hash_tag_list)

                
####TWITTER LISTENER CLASS####
class TwitterListener(StreamListener):
    """
    this is a basic listener class that just prints the tweets to console
    """
    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename
        
    def on_data(self, data): #class object thus takes self as argument 
        try:
            print(data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(data)
            return True
        except BaseException as e:
            print("Error on data: %s" % str(e))
        return True
        
    def on_error(self,status):
        if status == 420:
            #returning false on_data method of rate limit exceeds
            return False
        print(status)
        
        
####TWEETS ANALYSER####
class  TweetAnalyser():
    """
    provides functionality for analysing and categorizing content from tweets
    """
    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za_z0-9]+)|([^0-9A-za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
    
    def analyze_sentiment(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))
        
        if analysis.sentiment.polarity > 0:
            return 1
        elif analysis.sentiment.polarity == 0:
            return 0
        else:
            return -1
    
    def tweets_to_data_frame(self, tweets):
        df = pd.DataFrame(data = [tweet.text for tweet in tweets], columns = ['Tweets'])
        #df['Source'] = np.array([tweet.source for tweet in tweets])
        df['ReTweets'] = np.array([tweet.retweet_count for tweet in tweets])
        df['Likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['Date'] = np.array([tweet.created_at for tweet in tweets])
        df['Length'] = np.array([len(tweet.text) for tweet in tweets])
        return df
    

####MAIN CLASS####
if __name__ == "__main__":
    
    twitter_client = TwitterClient()
    tweets_analyser = TweetAnalyser()
    api = twitter_client.get_twitter_client_api()    
    tweets = api.user_timeline(screen_name ="realDonaldTrump", count = 200)
    
    #to list the directory 
    #print(dir(tweets[0])) 
    
    #defining the dataframefor tweets
    df = tweets_analyser.tweets_to_data_frame(tweets)
    df['Sentiment'] = np.array([tweets_analyser.analyze_sentiment(tweet) for tweet in df['Tweets']])
    print(df.head(100))


    
    #printing the mean of the length functionality
    #print(np.mean(df['Length']))

    #plottinf the time series grap wuth the number of likes and number of retweets
    #Time series 
    #time_likes = pd.Series(data = df['Likes'].values, index = df['Date'])
    #time_likes.plot(figsize = (10, 5), label="likes", legend = True)
    #time_retweets = pd.Series(data = df['ReTweets'].values, index = df['Date'])
    #time_retweets.plot(figsize = (10, 5), label="retweets", legend = True)
    #plt.show()
