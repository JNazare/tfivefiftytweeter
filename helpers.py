from datetime import datetime, timedelta
from email.utils import parsedate_tz
import json
from bson import json_util
from bson.json_util import dumps
from bson.json_util import loads

raw_hashtag = "t550tweeter"

def datetimeformat(value, format='%H:%M'):
    return value.strftime(format)

def to_datetime(datestring):
    time_tuple = parsedate_tz(datestring.strip())
    dt = datetime(*time_tuple[:6])
    return dt - timedelta(seconds=time_tuple[-1])

def formatDateTimeofTweet(tweet):
    tweet["created_at"] = to_datetime(tweet["created_at"]) - timedelta(hours=4)
    tweet["created_at_str"] = datetimeformat(tweet["created_at"])
    return tweet

def tagQuestioninTweet(tweet):
    tweet["is_question"]=False
    if "?" in tweet["text"]:
        tweet["is_question"]=True
    return tweet

def tagAuthorinTweet(tweet, session):
    tweet["is_author"]=False
    if int(tweet["user_id"])==session["id_str"]:
        tweet["is_author"]=True
    return tweet

def addTweetToDict(organizedHashtags, tweet, hashtagString):
    if organizedHashtags.get(hashtagString, None) != None:
        organizedHashtags[hashtagString]["tweets"].append(tweet)
        organizedHashtags[hashtagString]["user_photos"].append(tweet["user_profile_image_url"])
        if organizedHashtags[hashtagString]["is_author"] == False and tweet["is_author"]==True:
            organizedHashtags[hashtagString]["is_author"] = True
    else:
        organizedHashtags[hashtagString] = {"tweets": [tweet], "user_photos": 
                                            [tweet["user_profile_image_url"]], 
                                            "total_favorites": int(tweet["favorite_count"]),
                                            "is_author": tweet["is_author"]}
    return organizedHashtags

def sortHashtagsinTweet(tweet):
    hashtagArray = tweet.get("hashtags", None)
    for hashtag in hashtagArray:
        tweet["text"] = tweet["text"].replace("#"+hashtag, "")
    hashtagArray.remove(raw_hashtag)
    hashtagArray.sort()
    hashtagString = " ".join(hashtagArray)
    return [tweet, hashtagString]

def sortHashtagstoList(organizedHashtags):
    hashtagList = []
    for hashtag in organizedHashtags:
        hashtagList.append(organizedHashtags[hashtag])
    hashtagList.sort(key=lambda x: x["most_recent"], reverse=True)
    return hashtagList

def sortTweets(tweets, session):
    organizedHashtags = {}
    for tweet in tweets:
        [tweet, hashtagString] = sortHashtagsinTweet(tweet)
        tweet = formatDateTimeofTweet(tweet)
        tweet["_id"] = str(tweet["_id"])
        tweet = tagQuestioninTweet(tweet)
        tweet = tagAuthorinTweet(tweet, session)
        organizedHashtags = addTweetToDict(organizedHashtags, tweet, hashtagString)
    for hashtagString in organizedHashtags.keys():
        organizedHashtags[hashtagString]["user_photos"]=list(set(organizedHashtags[hashtagString]["user_photos"]))
        organizedHashtags[hashtagString]["tweets"].sort(key=lambda x: x["created_at"], reverse=True)
        organizedHashtags[hashtagString]["most_recent"]=organizedHashtags[hashtagString]["tweets"][0]["created_at"]
        organizedHashtags[hashtagString]["hashtagString"] = hashtagString
        organizedHashtags[hashtagString]["raw_data"]=json.dumps(organizedHashtags[hashtagString], default=json_util.default)
    hashtagList = sortHashtagstoList(organizedHashtags)
    return hashtagList 
