import os, requests, sys
import requests_oauthlib

try:
    import urllib.parse
    quote = urllib.parse.quote
except ImportError:
    import urlib
    quote = urllib.quote

TWITTER_KEY    = os.environ["TWITTER_KEY"]
TWITTER_SECRET = os.environ["TWITTER_SECRET"]

def make_oauth(resource_owner_key, resource_owner_secret):
    return OAuth1Session(
        TWITTER_KEY,
        client_secret=TWITTER_SECRET,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
    )

def request_token(callback_uri):
    ''': (...) -> (AuthorizationUrl, ResourceOwnerKey, ResourceOwnerSecret)'''

    oauth = requests_oauthlib.OAuth1Session(
        TWITTER_KEY,
        client_secret=TWITTER_SECRET,
        callback_uri=callback_uri,
    )

    url = "https://api.twitter.com/oauth/request_token"
    response = oauth.fetch_request_token(url)
    resource_owner_key    = response["oauth_token"]
    resource_owner_secret = response["oauth_token_secret"]

    url = "https://api.twitter.com/oauth/authorize"
    authorization_url = oauth.authorization_url(url)

    return (
        authorization_url,
        resource_owner_key,
        resource_owner_secret,
    )

def access_token(verifier, resource_owner_key, resource_owner_secret):
    ''': (...) -> (ResourceOwnerKey, ResourceOwnerSecret)'''

    oauth = requests_oauthlib.OAuth1Session(
        TWITTER_KEY,
        client_secret=TWITTER_SECRET,
    )
    response = oauth.parse_authorization_response(verifier)
    verifier = response["oauth_verifier"]

    oauth = OAuth1Session(
        TWITTER_KEY,
        client_secret=TWITTER_SECRET,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        verifier=verifier,
    )
    url = "https://api.twitter.com/oauth/access_token"
    access = oauth.fetch_access_token(url)

    resource_owner_key    = response["oauth_token"]
    resource_owner_secret = response["oauth_token_secret"]
    return (
        resource_owner_key,
        resource_owner_secret,
    )
