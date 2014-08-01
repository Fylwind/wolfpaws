import os
from flask import Flask, redirect, request, url_for

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

@app.route('/facts')
def dummy():
    return 'Nevy secretly likes green~ :3'
