import json, os, random
from flask import Flask, redirect, request, session, url_for
import twitter

app = Flask(__name__)
app.debug = bool(os.environ.get("DEBUG", False))
app.secret_key = os.environ["SESSION_SECRET"]
app.url_map.strict_slashes = False
BASE_URL = os.environ["BASE_URL"]
random.seed()

if app.debug:
    JSON_FORMAT = {"sort_keys": True, "indent": 4, "separators": (",", ": ")}
    BASE_URL = "http://localhost:5000"

@app.before_request
def remove_trailing_slash():
    if len(request.path) != 1 and request.path.endswith("/"):
        return redirect(request.path[:-1])

@app.route("/")
def main():
    return ":3"

@app.route("/fav", methods=("GET", "POST"))
def fav():

    if request.method == "GET":
        verifier = request.args.get("oauth_verifier", None)
        if verifier:
            # what if they don't exist?
            key = session["fav/key"]
            secret = session["fav/secret"]
            session["fav/access_key"], session["fav/access_secret"] = \
                twitter.access_token(verifier, key, secret)

            oauth = twitter.make_oauth(session["fav/access_key"],
                                       session["fav/access_secret"])
            params = {
                "include_entities": False,
                "skip_status": True,
            }
            url = "https://api.twitter.com/1.1/account/verify_credentials.json"
            response = oauth.get(url=url, params=params)
            session["fav/src"] = json.loads(response.text)["screen_name"]

            return redirect("/fav")

        if "fav/access_key" not in session:
            return """<a href="/fav/login">Log In</a>"""

        return """
<p>This will refavorite all (up to at most 14) tweets from the Target user, provided that the tweets are within 200 of your most recent Tweets.</p>

<p><strong>Due to API limitations, you can only Unfavorite/Favorite at most 15
tweets every 15 minutes.</strong></p>

<form class="search" method="post" action="/fav">
  <p>Target username:
  <input type="text" name="dest" placeholder="JohnSmith"/></p>
  <button name="action" value="gather">Gather Tweets</button>
  <button name="action" value="unfav">Unfavorite</button>
  <button name="action" value="fav">Favorite</button>
</form>
<a href="/fav/logout">Log Out</a>
"""

    elif request.method == "POST":

        oauth = twitter.make_oauth(session["fav/access_key"],
                                   session["fav/access_secret"])
        action = request.form["action"]
        dest_user = request.form["dest"].lower().lstrip("@")
        src_user = session["fav/src"]

        LIMIT = 15
        if action == "gather":

            params = {
                "screen_name": src_user,
                "count": 200,
                "include_entities": False,
            }
            url = "https://api.twitter.com/1.1/favorites/list.json"
            response = oauth.get(url=url, params=params)
            tweets = json.loads(response.text)

            tweet_ids = []
            for tweet in tweets:
                if (len(tweet_ids) < LIMIT and "@" not in tweet["text"] and
                    tweet["user"]["screen_name"].lower() == dest_user):
                    tweet_ids.append(str(tweet["id"]))

            session["fav/tweet-ids"] = ",".join(tweet_ids)
            return ("gathered {0} of {1}'s tweets (now go back and click Unfavorite; no need to re-enter the username again)"
                    .format(len(tweet_ids), dest_user))

        elif action == "unfav":
            tweet_ids = session["fav/tweet-ids"].split(",")
            for tweet_id in tweet_ids:
                params = {
                    "id": tweet_id,
                    "include_entities": False,
                }
                url = "https://api.twitter.com/1.1/favorites/destroy.json"
                response = oauth.post(url=url, params=params)
                if app.debug:
                    app.logger.debug(tweet_id)
            return ("unfavorited {0} of {1}'s tweets (now go back and click Favorite; no need to re-enter the username again)"
                    .format(len(tweet_ids), dest_user))

        elif action == "fav":
            tweet_ids = session["fav/tweet-ids"].split(",")
            for tweet_id in tweet_ids:
                params = {
                    "id": tweet_id,
                    "include_entities": False,
                }
                url = "https://api.twitter.com/1.1/favorites/create.json"
                response = oauth.post(url=url, params=params)
                if app.debug:
                    app.logger.debug(tweet_id)
            return ("favorited {0} of {1}'s tweets (tada!)"
                    .format(len(tweet_ids), dest_user))

@app.route("/fav/login")
def favlogin():
    callback_uri = BASE_URL + "/fav"
    result = twitter.request_token(callback_uri)
    authorization_url = result[0]
    session["fav/key"], session["fav/secret"] = result[1:]
    return redirect(authorization_url)

@app.route("/fav/logout")
def favlogout():
    session.pop("fav/key", None)
    session.pop("fav/secret", None)
    session.pop("fav/access_key", None)
    session.pop("fav/access_secret", None)
    return redirect("/fav")

@app.route("/facts")
def facts():
    facts = (
        "Nevy secretly likes green~ :3",
        "Syfaro is a purple fox! *yiff yiff*",
        "Kyash is the most innocent walf :D",
        "Try pressing F5 again.",
    )
    return random.choice(facts)
