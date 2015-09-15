import sys
import tweepy
import json
import keys
from pymongo import MongoClient

TRACKED_HASHTAG='#classtweeter'

CONSUMER_TOKEN=keys.CONSUMER_TOKEN
CONSUMER_SECRET=keys.CONSUMER_SECRET
MY_ACCESS_TOKEN=keys.MY_ACCESS_TOKEN
MY_ACCESS_SECRET=keys.MY_ACCESS_SECRET

auth = tweepy.OAuthHandler(CONSUMER_TOKEN, CONSUMER_SECRET)
auth.set_access_token(MY_ACCESS_TOKEN, MY_ACCESS_SECRET)
api = tweepy.API(auth)

### MONGO CONNECTION ###
def connect():
    connection = MongoClient(keys.MONGO_KEYS[0], keys.MONGO_KEYS[1])
    handle = connection[keys.MONGO_KEYS[2]]
    handle.authenticate(keys.MONGO_KEYS[3], keys.MONGO_KEYS[4])
    return handle

handle = connect()
twitter_collection = handle.collected_tweets

class CustomStreamListener(tweepy.StreamListener):
    # ...
    def on_status(self, status):
            try:
                savejson = {}
                twitter_json = status._json
                hashtag_list = []
                for hashtag in twitter_json["entities"]["hashtags"]:
                    hashtag_list.append(str(hashtag["text"]))
                savejson["text"] = str(twitter_json["text"])
                savejson["favorite_count"] = str(twitter_json["favorite_count"])
                savejson["hashtags"] = hashtag_list
                savejson["id"] = str(twitter_json["id_str"])
                savejson["user_id"]= str(twitter_json["user"]["id_str"])
                savejson["user_profile_image_url"]=str(twitter_json["user"]["profile_image_url"])
                savejson["created_at"]=str(twitter_json["created_at"])
                tweet_id = twitter_collection.insert(savejson)
            except:
                # Catch any unicode errors while printing to console
                # and just ignore them to avoid breaking application.
                pass

stream = tweepy.Stream(auth, CustomStreamListener(), timeout=None, compression=True)
stream.filter(track=[TRACKED_HASHTAG])