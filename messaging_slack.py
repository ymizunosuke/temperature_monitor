import json
import os
import urllib.request


def notice(message):
    data = {
            'text': message,
    }
    headers = {
            'Content-type': 'application/json'
    }

    req = urllib.request.Request(os.environ['SLACK_URL'], json.dumps(data).encode(), headers)
    urllib.request.urlopen(req)
