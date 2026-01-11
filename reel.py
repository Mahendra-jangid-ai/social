# from flask import Flask, redirect, request, render_template_string
# import requests, time, os, urllib.parse

# app = Flask(__name__)

# APP_ID="1373679344772221"
# APP_SECRET="db7320b326768fbafef4315ed9736c60"
# REDIRECT_URI = "http://localhost:5000/callback"

# SCOPES = [
#     "pages_show_list",
#     "instagram_basic",
#     "instagram_content_publish",
#     "business_management"
# ]

# # -------------------- LOGIN --------------------
# @app.route("/")
# def home():
#     params = {
#         "client_id": APP_ID,
#         "redirect_uri": REDIRECT_URI,
#         "scope": ",".join(SCOPES),
#         "response_type": "code"
#     }
#     url = "https://www.facebook.com/v19.0/dialog/oauth?" + urllib.parse.urlencode(params)
#     return f'<h2>Instagram Manager</h2><a href="{url}">Login with Facebook</a>'

# # -------------------- CALLBACK --------------------
# @app.route("/callback")
# def callback():
#     code = request.args.get("code")

#     token = requests.get(
#         "https://graph.facebook.com/v19.0/oauth/access_token",
#         params={
#             "client_id": APP_ID,
#             "client_secret": APP_SECRET,
#             "redirect_uri": REDIRECT_URI,
#             "code": code
#         }
#     ).json()["access_token"]

#     pages = requests.get(
#         "https://graph.facebook.com/v19.0/me/accounts",
#         params={"access_token": token}
#     ).json()["data"]

#     page_id = pages[0]["id"]
#     page_token = pages[0]["access_token"]

#     ig = requests.get(
#         f"https://graph.facebook.com/v19.0/{page_id}",
#         params={
#             "fields": "instagram_business_account",
#             "access_token": page_token
#         }
#     ).json()

#     ig_id = ig["instagram_business_account"]["id"]

#     return render_template_string("""
#     <h2>Connected</h2>
#     <b>Instagram ID:</b> {{ig_id}}<br><br>

#     <form method="post" action="/publish">
#         <input type="hidden" name="ig_id" value="{{ig_id}}">
#         <input type="hidden" name="token" value="{{page_token}}">

#         Media URL (Image or MP4):<br>
#         <input type="text" name="url" size="80"><br><br>

#         Caption:<br>
#         <textarea name="caption" rows="4" cols="80"></textarea><br><br>

#         Type:
#         <select name="type">
#             <option value="image">Image Post</option>
#             <option value="video">Reel Video</option>
#         </select><br><br>

#         <button type="submit">Publish</button>
#     </form>
#     """, ig_id=ig_id, page_token=page_token)

# # -------------------- PUBLISH --------------------
# @app.route("/publish", methods=["POST"])
# def publish():
#     ig_id = request.form["ig_id"]
#     token = request.form["token"]
#     url = request.form["url"]
#     caption = request.form["caption"]
#     mtype = request.form["type"]

#     data = {
#         "caption": caption,
#         "access_token": token
#     }

#     if mtype == "image":
#         data["image_url"] = url

#     if mtype == "video":
#         data["media_type"] = "REELS"
#         data["video_url"] = url

#     create = requests.post(
#         f"https://graph.facebook.com/v19.0/{ig_id}/media",
#         data=data
#     ).json()

#     if "id" not in create:
#         return f"<pre>Error: {create}</pre>"

#     creation_id = create["id"]

#     if mtype == "video":
#         while True:
#             status = requests.get(
#                 f"https://graph.facebook.com/v19.0/{creation_id}",
#                 params={
#                     "fields": "status_code",
#                     "access_token": token
#                 }
#             ).json()
#             if status.get("status_code") == "FINISHED":
#                 break
#             time.sleep(3)

#     publish = requests.post(
#         f"https://graph.facebook.com/v19.0/{ig_id}/media_publish",
#         data={
#             "creation_id": creation_id,
#             "access_token": token
#         }
#     ).json()

#     return f"<h3>Posted Successfully</h3><pre>{publish}</pre>"

# # -------------------- RUN --------------------
# if __name__ == "__main__":
#     app.run(debug=True)




from flask import Flask, redirect, request, render_template_string
import requests, time, threading, datetime, urllib.parse

app = Flask(__name__)

APP_ID="1373679344772221"
APP_SECRET="db7320b326768fbafef4315ed9736c60"
REDIRECT_URI = "http://localhost:5000/callback"

SCOPES = [
    "pages_show_list",
    "instagram_basic",
    "instagram_content_publish",
    "business_management"
]

# ---------------- LOGIN ----------------
@app.route("/")
def home():
    params = {
        "client_id": APP_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": ",".join(SCOPES),
        "response_type": "code"
    }
    url = "https://www.facebook.com/v19.0/dialog/oauth?" + urllib.parse.urlencode(params)
    return f'<h2>Instagram Auto Scheduler</h2><a href="{url}">Login with Facebook</a>'

# ---------------- CALLBACK ----------------
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
    ).json()["access_token"]

    pages = requests.get(
        "https://graph.facebook.com/v19.0/me/accounts",
        params={"access_token": token}
    ).json()["data"]

    page_token = pages[0]["access_token"]
    page_id = pages[0]["id"]

    ig = requests.get(
        f"https://graph.facebook.com/v19.0/{page_id}",
        params={"fields":"instagram_business_account","access_token":page_token}
    ).json()

    ig_id = ig["instagram_business_account"]["id"]

    return render_template_string("""
    <h2>Schedule Multiple Posts</h2>

    <form method="post" action="/schedule">

    {% for i in range(1,5) %}
    <h4>Post {{i}}</h4>
    Media URL: <input name="url{{i}}" size="70"><br>
    Caption: <textarea name="caption{{i}}"></textarea><br>
    Type:
    <select name="type{{i}}">
        <option value="image">Image</option>
        <option value="video">Reel</option>
    </select><br>
    Date Time (YYYY-MM-DD HH:MM):
    <input name="time{{i}}" placeholder="2026-01-12 18:30"><br><br>
    {% endfor %}

    <input type="hidden" name="ig_id" value="{{ig_id}}">
    <input type="hidden" name="token" value="{{page_token}}">

    <button type="submit">Start Auto Scheduler</button>
    </form>
    """, ig_id=ig_id, page_token=page_token)

# ---------------- BACKGROUND PUBLISHER ----------------
def publish_job(delay, ig_id, token, url, caption, mtype):
    time.sleep(delay)

    data = {
        "caption": caption,
        "access_token": token
    }

    if mtype == "image":
        data["image_url"] = url
    else:
        data["media_type"] = "REELS"
        data["video_url"] = url

    create = requests.post(
        f"https://graph.facebook.com/v19.0/{ig_id}/media",
        data=data
    ).json()

    if "id" not in create:
        print("Create Error:", create)
        return

    creation_id = create["id"]

    if mtype == "video":
        while True:
            status = requests.get(
                f"https://graph.facebook.com/v19.0/{creation_id}",
                params={"fields":"status_code","access_token":token}
            ).json()
            if status.get("status_code") == "FINISHED":
                break
            time.sleep(5)

    publish = requests.post(
        f"https://graph.facebook.com/v19.0/{ig_id}/media_publish",
        data={"creation_id":creation_id,"access_token":token}
    ).json()

    print("✅ Auto Published:", publish)

# ---------------- SCHEDULER ----------------
@app.route("/schedule", methods=["POST"])
def schedule():
    ig_id = request.form["ig_id"]
    token = request.form["token"]

    for i in range(1,5):
        url = request.form.get(f"url{i}")
        caption = request.form.get(f"caption{i}")
        mtype = request.form.get(f"type{i}")
        time_str = request.form.get(f"time{i}")

        if not url or not time_str:
            continue

        post_time = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M")
        delay = (post_time - datetime.datetime.now()).total_seconds()

        t = threading.Thread(
            target=publish_job,
            args=(delay, ig_id, token, url, caption, mtype)
        )
        t.start()

    return "<h3>All Posts Scheduled Successfully 🚀</h3>"

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
