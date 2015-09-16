from flask import Flask, Response, session, render_template, redirect, request, url_for
import flask
from functools import wraps
import tweepy
import keys
from operator import itemgetter
from pymongo import MongoClient
from bson import json_util
from bson.json_util import dumps
from bson.json_util import loads
import json
import re
from datetime import datetime, timedelta
from email.utils import parsedate_tz
import helpers

app = Flask(__name__)
app.secret_key = 'shhhhhh'
app.config['SERVER_NAME'] = 'localhost:5000'
consumer_token = keys.CONSUMER_TOKEN
consumer_secret = keys.CONSUMER_SECRET

@app.template_filter('strftime')
def datetimeformat(value, format='%H:%M'):
    return value.strftime(format)

@app.template_filter('hashtagToGroupname')
def hashtagToGroupname(hashtag):
    # print hashtag
    return hashtag.replace("_", " ")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("oauth_verifier", None) is None:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def getAPI():
    key = session["access_token_key"]
    secret = session["access_token_secret"]
    auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
    auth.set_access_token(key, secret)
    api = tweepy.API(auth)
    if session.get("id_str", None) == None:
        session["id_str"] = api.me().id
    return api

def connect():
    connection = MongoClient(keys.MONGO_KEYS[0], keys.MONGO_KEYS[1])
    handle = connection[keys.MONGO_KEYS[2]]
    handle.authenticate(keys.MONGO_KEYS[3], keys.MONGO_KEYS[4])
    return handle

@app.route('/')
@login_required
def index():
    getAPI()
    tweets = dumps(list(connect().collected_tweets.find()))
    organizedTweets = helpers.sortTweets(loads(tweets), session)
    return flask.render_template('index.html', groups=organizedTweets, focus_group=organizedTweets[0])

@app.route('/request_url')
def login():
    callback_url = "http://localhost:5000/callback"
    auth = tweepy.OAuthHandler(consumer_token, consumer_secret, callback_url)
    redirect_url = auth.get_authorization_url()
    session["key"] = auth.request_token.key
    session["secret"] = auth.request_token.secret

    # redirect user
    return redirect(redirect_url)

@app.route('/callback')
def callback():
    
    session["oauth_verifier"] = request.args.get('oauth_verifier', '')
    session["oauth_token"] = request.args.get("oauth_token", "")

    key = session["key"]
    secret = session["secret"]
    code = session["oauth_verifier"]

    # create OAuth object
    auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
    auth.set_request_token(key, secret)

    # exchange the authentication token
    try:
        auth.get_access_token(code)
        session["access_token_key"] = auth.access_token.key
        session["access_token_secret"] = auth.access_token.secret
    except tweepy.TweepError:
        print 'Error! Failed to get access token.'

    return redirect(url_for('index'))

@app.route('/refresh')
@login_required
def refresh():
    handle = connect()
    tweets = dumps(list(handle.collected_tweets.find()))
    organizedTweets = helpers.sortTweets(loads(tweets), session)
    return render_template('tweetcard.html', groups=organizedTweets)#, render_template('sidebar-content.html', focus_group=organizedTweets[0])

@app.route('/refresh_sidebar')
@login_required
def refresh_sidebar():
    group = request.args.get("focused_group", None)
    handle = connect()
    tweets = dumps(list(handle.collected_tweets.find()))
    organizedTweets = helpers.sortTweets(loads(tweets), session)
    focused_info = None
    for grouping in organizedTweets:
        if group == grouping["hashtagString"]:
            focused_info = grouping
    return render_template('sidebar-content.html', focus_group=focused_info)

@app.route("/sendToTwitter", methods=['POST'])
@login_required
def sendToTwitter():
    text = request.form.to_dict().keys()[0]
    api = getAPI()
    api.update_status(text)
    return 'done'

@app.route('/focus', methods=['POST'])
@login_required
def focus():
    return render_template('sidebar-content.html', focus_group=request.json)

@app.route('/help')
@login_required
def help():
    return render_template('help.html')


if __name__ == '__main__':
    app.run(debug=True)
