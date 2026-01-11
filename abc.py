import os
from flask import Flask, request
import requests, urllib.parse

app = Flask(__name__)

APP_ID = os.environ.get("APP_ID")
APP_SECRET = os.environ.get("APP_SECRET")
REDIRECT_URI = 'https://social-1-shd.onrender.com/callback'

SCOPES = ["instagram_basic", "pages_show_list", "business_management"]

@app.route("/")
def index():
    params = {
        "client_id": APP_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": ",".join(SCOPES),
        "response_type": "code"
    }
    url = "https://www.facebook.com/v19.0/dialog/oauth?" + urllib.parse.urlencode(params)
    return f"<h2>Instagram Business Login</h2><a href='{url}'>Login with Facebook</a>"

@app.route("/callback")
def callback():
    code = request.args.get("code")

    token = requests.get(
        "https://graph.facebook.com/v19.0/oauth/access_token",
        params={
            "client_id": APP_ID,
            "client_secret": APP_SECRET,
            "redirect_uri": REDIRECT_URI,
            "code": code
        }
    ).json()

    access_token = token["access_token"]

    pages = requests.get(
        "https://graph.facebook.com/v19.0/me/accounts",
        params={"access_token": access_token}
    ).json()

    page_id = pages["data"][0]["id"]

    ig = requests.get(
        f"https://graph.facebook.com/v19.0/{page_id}",
        params={
            "fields": "instagram_business_account",
            "access_token": access_token
        }
    ).json()

    ig_user_id = ig["instagram_business_account"]["id"]

    media = requests.get(
        f"https://graph.facebook.com/v19.0/{ig_user_id}/media",
        params={
            "fields": "id,media_type,media_url,caption,timestamp",
            "access_token": access_token
        }
    ).json()

    return {
        "access_token": access_token,
        "page_id": page_id,
        "instagram_user_id": ig_user_id,
        "media": media
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
