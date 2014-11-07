import os
from flask import Flask, redirect, request, url_for
import twitter

app = Flask(__name__)
if os.path.exists("DEBUG"):
    app.debug = True
app.url_map.strict_slashes = False

@app.before_request
def remove_trailing_slash():
    if len(request.path) != 1 and request.path.endswith('/'):
        return redirect(request.path[:-1])

@app.route('/')
def main():
    return 'Woot, it works!'

@app.route('/fav')
def fav():
    if request.method == "GET":
        token = request.args["oauth_token"]
        verifier = request.args["oauth_verifier"]
        return s
    return "???"

@app.route('/favlogin')
def favlogin():
    callback_uri = "http://wolfpa.ws/fav"
    if app.debug:
        callback_uri = "http://localhost:5000/fav"
    result = twitter.request_token(callback_uri)
    authorization_url = result[0]
    return redirect(authorization_url)

@app.route('/facts')
def dummy():
    return 'Nevy secretly likes green~ :3'
