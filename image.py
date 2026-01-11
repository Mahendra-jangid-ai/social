# # app.py

# from flask import Flask, redirect, request
# import requests
# import urllib.parse
# import os

# app = Flask(__name__)

# APP_ID = "1373679344772221"
# APP_SECRET = "db7320b326768fbafef4315ed9736c60"
# REDIRECT_URI = "http://localhost:5000/callback"
# SCOPES = ["instagram_basic", "pages_show_list", "business_management"]

# SAVE_DIR = "instagram_media"
# os.makedirs(SAVE_DIR, exist_ok=True)

# @app.route("/")
# def login():
#     params = {
#         "client_id": APP_ID,
#         "redirect_uri": REDIRECT_URI,
#         "scope": ",".join(SCOPES),
#         "response_type": "code",
#         "state": "secure123"
#     }
#     login_url = "https://www.facebook.com/v19.0/dialog/oauth?" + urllib.parse.urlencode(params)
#     return f'<h2>Instagram Business Login</h2><a href="{login_url}">Login with Facebook</a>'

# @app.route("/callback")
# def callback():
#     code = request.args.get("code")

#     # 1. Exchange code for access token
#     token_url = "https://graph.facebook.com/v19.0/oauth/access_token"
#     token_params = {
#         "client_id": APP_ID,
#         "client_secret": APP_SECRET,
#         "redirect_uri": REDIRECT_URI,
#         "code": code
#     }
#     token_res = requests.get(token_url, params=token_params).json()
#     access_token = token_res["access_token"]

#     # 2. Get Facebook Pages
#     pages_url = "https://graph.facebook.com/v19.0/me/accounts"
#     pages_res = requests.get(pages_url, params={"access_token": access_token}).json()
#     page_id = pages_res["data"][0]["id"]

#     # 3. Get Instagram Business Account
#     ig_url = f"https://graph.facebook.com/v19.0/{page_id}"
#     ig_params = {
#         "fields": "instagram_business_account",
#         "access_token": access_token
#     }
#     ig_res = requests.get(ig_url, params=ig_params).json()
#     ig_user_id = ig_res["instagram_business_account"]["id"]

#     # 4. Fetch all Instagram media (with pagination)
#     media_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media"
#     params = {
#         "fields": "id,caption,media_type,media_url,timestamp",
#         "access_token": access_token,
#         "limit": 25
#     }

#     all_media = []

#     while True:
#         res = requests.get(media_url, params=params).json()
#         data = res.get("data", [])
#         all_media.extend(data)

#         # Download images
#         for item in data:
#             if item["media_type"] in ["IMAGE", "CAROUSEL_ALBUM"]:
#                 img_url = item["media_url"]
#                 img_bytes = requests.get(img_url).content
#                 file_path = os.path.join(SAVE_DIR, f"{item['id']}.jpg")
#                 with open(file_path, "wb") as f:
#                     f.write(img_bytes)

#         # Pagination
#         paging = res.get("paging", {})
#         if "next" in paging:
#             media_url = paging["next"]
#             params = {}
#         else:
#             break

#     return {
#         "access_token": access_token,
#         "page_id": page_id,
#         "instagram_user_id": ig_user_id,
#         "total_posts": len(all_media),
#         "download_folder": SAVE_DIR,
#         "media_sample": all_media[:5]
#     }

# if __name__ == "__main__":
#     app.run(debug=True)


from flask import Flask, redirect, request
import requests
import urllib.parse
import os

app = Flask(__name__)

APP_ID = "1373679344772221"
APP_SECRET = "db7320b326768fbafef4315ed9736c60"
REDIRECT_URI = "http://localhost:5000/callback"
SCOPES = ["instagram_basic", "pages_show_list", "business_management", "instagram_content_publish"]

SAVE_DIR = "instagram_media"
os.makedirs(SAVE_DIR, exist_ok=True)

@app.route("/")
def login():
    params = {
        "client_id": APP_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": ",".join(SCOPES),
        "response_type": "code",
        "state": "secure123"
    }
    login_url = "https://www.facebook.com/v19.0/dialog/oauth?" + urllib.parse.urlencode(params)
    return f'''
    <h2>Instagram Business Login</h2>
    <a href="{login_url}">Login with Facebook</a>
    '''

@app.route("/callback")
def callback():
    code = request.args.get("code")

    # 1. Exchange code for access token
    token_url = "https://graph.facebook.com/v19.0/oauth/access_token"
    token_params = {
        "client_id": APP_ID,
        "client_secret": APP_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": code
    }
    token_res = requests.get(token_url, params=token_params).json()
    access_token = token_res["access_token"]

    # 2. Get Facebook Pages
    pages_url = "https://graph.facebook.com/v19.0/me/accounts"
    pages_res = requests.get(pages_url, params={"access_token": access_token}).json()
    page_id = pages_res["data"][0]["id"]

    # 3. Get Instagram Business Account
    ig_url = f"https://graph.facebook.com/v19.0/{page_id}"
    ig_params = {
        "fields": "instagram_business_account",
        "access_token": access_token
    }
    ig_res = requests.get(ig_url, params=ig_params).json()
    ig_user_id = ig_res["instagram_business_account"]["id"]

    # 4. UI to publish post
    return f'''
    <h2>Connected Successfully</h2>
    <b>Access Token:</b><pre>{access_token}</pre>
    <b>Page ID:</b> {page_id}<br>
    <b>Instagram Business ID:</b> {ig_user_id}<br><br>

    <h3>Publish New Post</h3>
    <form action="/publish" method="post">
        <input type="hidden" name="access_token" value="{access_token}">
        <input type="hidden" name="ig_user_id" value="{ig_user_id}">
        Image URL (public https):<br>
        <input type="text" name="image_url" size="80"><br><br>
        Caption:<br>
        <textarea name="caption" rows="4" cols="80"></textarea><br><br>
        <button type="submit">🚀 Publish to Instagram</button>
    </form>
    '''

@app.route("/publish", methods=["POST"])
def publish():
    access_token = request.form["access_token"]
    ig_user_id = request.form["ig_user_id"]
    image_url = request.form["image_url"]
    caption = request.form["caption"]

    # Step 1: Create media container
    create_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media"
    create_res = requests.post(create_url, data={
        "image_url": image_url,
        "caption": caption,
        "access_token": access_token
    }).json()

    if "id" not in create_res:
        return f"<pre>Media Create Error: {create_res}</pre>"

    creation_id = create_res["id"]

    # Step 2: Publish media
    publish_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media_publish"
    publish_res = requests.post(publish_url, data={
        "creation_id": creation_id,
        "access_token": access_token
    }).json()

    return f'''
    <h2>🎉 Post Published Successfully</h2>
    <pre>{publish_res}</pre>
    <a href="/">Post Another</a>
    '''

if __name__ == "__main__":
    app.run(debug=True)
