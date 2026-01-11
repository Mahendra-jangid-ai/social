# # import os
# # import requests
# # from flask import Flask, redirect, request
# # from dotenv import load_dotenv

# # load_dotenv()

# # app = Flask(__name__)

# # FB_APP_ID = os.getenv("FB_APP_ID")
# # FB_APP_SECRET = os.getenv("FB_APP_SECRET")
# # REDIRECT_URI = os.getenv("REDIRECT_URI")

# # SCOPES = "pages_show_list,instagram_basic,instagram_content_publish"

# # @app.route("/")
# # def home():
# #     return """
# #     <h2>Instagram Connect</h2>
# #     <a href="/login">Connect with Facebook</a>
# #     """

# # @app.route("/login")
# # def login():
# #     fb_url = (
# #         "https://www.facebook.com/v18.0/dialog/oauth"
# #         f"?client_id={FB_APP_ID}"
# #         f"&redirect_uri={REDIRECT_URI}"
# #         f"&scope={SCOPES}"
# #     )
# #     return redirect(fb_url)

# # @app.route("/callback")
# # def callback():
# #     code = request.args.get("code")
# #     if not code:
# #         return "No code received from Facebook"

# #     # Exchange code for access token
# #     token_res = requests.get(
# #         "https://graph.facebook.com/v18.0/oauth/access_token",
# #         params={
# #             "client_id": FB_APP_ID,
# #             "client_secret": FB_APP_SECRET,
# #             "redirect_uri": REDIRECT_URI,
# #             "code": code,
# #         }
# #     ).json()

# #     if "access_token" not in token_res:
# #         return f"<pre>{token_res}</pre>"

# #     access_token = token_res["access_token"]

# #     # Fetch pages
# #     pages = requests.get(
# #         "https://graph.facebook.com/v18.0/me/accounts",
# #         params={"access_token": access_token}
# #     ).json()

# #     ig_id = None
# #     page_id = None

# #     for page in pages.get("data", []):
# #         ig = requests.get(
# #             f"https://graph.facebook.com/v18.0/{page['id']}",
# #             params={
# #                 "fields": "instagram_business_account",
# #                 "access_token": access_token
# #             }
# #         ).json()

# #         if ig.get("instagram_business_account"):
# #             ig_id = ig["instagram_business_account"]["id"]
# #             page_id = page["id"]
# #             break

# #     # 🔥 FINAL OUTPUT (BROWSER ME DIKHEGA)
# #     return f"""
# #     <h2>✅ OAuth Success</h2>

# #     <b>Access Token:</b>
# #     <pre>{access_token}</pre>

# #     <b>Facebook Page ID:</b>
# #     <pre>{page_id}</pre>

# #     <b>Instagram Business Account ID:</b>
# #     <pre>{ig_id}</pre>
# #     """

# # if __name__ == "__main__":
# #     print("Server running...")
# #     app.run(debug=True)


# import os
# import requests
# from flask import Flask, redirect, request
# from dotenv import load_dotenv

# load_dotenv()

# app = Flask(__name__)

# FB_APP_ID = os.getenv("FB_APP_ID")
# FB_APP_SECRET = os.getenv("FB_APP_SECRET")
# REDIRECT_URI = os.getenv("REDIRECT_URI")

# SCOPES = "pages_show_list,instagram_basic,instagram_content_publish"

# @app.route("/")
# def home():
#     return """
#     <h2>Instagram Connect</h2>
#     <a href="/login">Connect with Facebook</a>
#     """

# @app.route("/login")
# def login():
#     fb_url = (
#         "https://www.facebook.com/v18.0/dialog/oauth"
#         f"?client_id={FB_APP_ID}"
#         f"&redirect_uri={REDIRECT_URI}"
#         f"&scope={SCOPES}"
#     )
#     return redirect(fb_url)

# @app.route("/callback")
# def callback():
#     code = request.args.get("code")
#     if not code:
#         return "No code received from Facebook"

#     # 🔹 STEP 1: Get access token
#     token_res = requests.get(
#         "https://graph.facebook.com/v18.0/oauth/access_token",
#         params={
#             "client_id": FB_APP_ID,
#             "client_secret": FB_APP_SECRET,
#             "redirect_uri": REDIRECT_URI,
#             "code": code,
#         }
#     ).json()

#     if "access_token" not in token_res:
#         return f"<pre>{token_res}</pre>"

#     access_token = token_res["access_token"]

#     # 🔹 STEP 2: DEBUG TOKEN (permissions)
#     debug = requests.get(
#         "https://graph.facebook.com/debug_token",
#         params={
#             "input_token": access_token,
#             "access_token": f"{FB_APP_ID}|{FB_APP_SECRET}"
#         }
#     ).json()

#     scopes = debug.get("data", {}).get("scopes", [])

#     # 🔹 STEP 3: Pages + IG
#     pages = requests.get(
#         "https://graph.facebook.com/v18.0/me/accounts",
#         params={"access_token": access_token}
#     ).json()

#     page_id = None
#     ig_id = None

#     for page in pages.get("data", []):
#         ig = requests.get(
#             f"https://graph.facebook.com/v18.0/{page['id']}",
#             params={
#                 "fields": "instagram_business_account",
#                 "access_token": access_token
#             }
#         ).json()

#         if ig.get("instagram_business_account"):
#             page_id = page["id"]
#             ig_id = ig["instagram_business_account"]["id"]
#             break

#     # 🔥 UI OUTPUT
#     permissions_html = "".join(
#         f"<li>✅ {p}</li>" for p in scopes
#     )

#     return f"""
#     <h2>✅ OAuth Success</h2>

#     <h3>🔑 Access Token</h3>
#     <pre style="background:#f4f4f4;padding:10px">{access_token}</pre>

#     <h3>📄 Connected Assets</h3>
#     <ul>
#         <li><b>Facebook Page ID:</b> {page_id}</li>
#         <li><b>Instagram Business ID:</b> {ig_id}</li>
#     </ul>

#     <h3>🛡 Permissions Granted by User</h3>
#     <ul>
#         {permissions_html}
#     </ul>

#     <h3>🎯 Your Control</h3>
#     <p>
#     You can now manage features based on these permissions.
#     If a permission is missing, related features must be disabled.
#     </p>
#     """

# if __name__ == "__main__":
#     print("Server running...")
#     app.run(debug=True)


# app.py
from flask import Flask, redirect, request, url_for
import requests
import urllib.parse

app = Flask(__name__)

APP_ID = "1373679344772221"
APP_SECRET = "db7320b326768fbafef4315ed9736c60"
REDIRECT_URI = "http://localhost:5000/callback"
SCOPES = ["instagram_basic", "pages_show_list", "business_management"]

@app.route("/")
def index():
    params = {
        "client_id": APP_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": ",".join(SCOPES),
        "response_type": "code",
        "state": "12345"
    }
    login_url = "https://www.facebook.com/v19.0/dialog/oauth?" + urllib.parse.urlencode(params)
    return f'<a href="{login_url}">Login with Facebook</a>'

@app.route("/callback")
def callback():
    code = request.args.get("code")

    token_url = "https://graph.facebook.com/v19.0/oauth/access_token"
    token_params = {
        "client_id": APP_ID,
        "client_secret": APP_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": code
    }
    token_res = requests.get(token_url, params=token_params).json()
    access_token = token_res["access_token"]

    # Step 1: Get Pages
    pages_url = "https://graph.facebook.com/v19.0/me/accounts"
    pages = requests.get(pages_url, params={"access_token": access_token}).json()

    page_id = pages["data"][0]["id"]

    # Step 2: Get Instagram Business Account
    ig_url = f"https://graph.facebook.com/v19.0/{page_id}"
    ig_params = {
        "fields": "instagram_business_account",
        "access_token": access_token
    }
    ig_data = requests.get(ig_url, params=ig_params).json()
    ig_user_id = ig_data["instagram_business_account"]["id"]

    # Step 3: Fetch Instagram Media
    media_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media"
    media_params = {
        "fields": "id,caption,media_type,media_url,timestamp",
        "access_token": access_token
    }
    media = requests.get(media_url, params=media_params).json()

    return {
        "access_token": access_token,
        "page_id": page_id,
        "instagram_user_id": ig_user_id,
        "media": media
    }

if __name__ == "__main__":
    app.run(debug=True)
