from flask import Flask, request, redirect, render_template_string, jsonify
import requests, datetime, threading, time, urllib.parse, uuid

app = Flask(__name__)

APP_ID = "1373679344772221"
APP_SECRET = "YOUR_APP_SECRET"
REDIRECT_URI = "http://localhost:5000/callback"
VERIFY_TOKEN = "mahi123"

# In production -> Redis / DB
SCHEDULED_JOBS = {}
PUBLISH_QUEUE = {}

SCOPES = "pages_show_list,instagram_basic,instagram_content_publish,business_management"

# ---------------- LOGIN ----------------
@app.route("/")
def home():
    url = "https://www.facebook.com/v19.0/dialog/oauth?" + urllib.parse.urlencode({
        "client_id": APP_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
        "response_type": "code"
    })
    return f"<h2>Instagram Scheduler</h2><a href='{url}'>Login with Facebook</a>"

# ---------------- CALLBACK ----------------
@app.route("/callback")
def callback():
    code = request.args.get("code")

    token = requests.get("https://graph.facebook.com/v19.0/oauth/access_token", params={
        "client_id": APP_ID,
        "client_secret": APP_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": code
    }).json()["access_token"]

    pages = requests.get("https://graph.facebook.com/v19.0/me/accounts",
        params={"access_token": token}).json()["data"]

    page = pages[0]
    page_token = page["access_token"]

    ig = requests.get(f"https://graph.facebook.com/v19.0/{page['id']}",
        params={"fields":"instagram_business_account","access_token":page_token}).json()

    ig_id = ig["instagram_business_account"]["id"]

    return render_template_string("""
    <h2>Schedule Posts</h2>
    <form method="post" action="/schedule">
    {% for i in range(1,5) %}
      <h4>Post {{i}}</h4>
      URL: <input name="url{{i}}" size="60"><br>
      Caption: <textarea name="caption{{i}}"></textarea><br>
      Type:
      <select name="type{{i}}">
        <option value="image">Image</option>
        <option value="reel">Reel</option>
      </select><br>
      Time (YYYY-MM-DD HH:MM):
      <input name="time{{i}}" placeholder="2026-01-12 18:30"><br><br>
    {% endfor %}
    <input type="hidden" name="ig_id" value="{{ig_id}}">
    <input type="hidden" name="token" value="{{page_token}}">
    <button>Schedule</button>
    </form>
    """, ig_id=ig_id, page_token=page_token)

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

        run_at = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M")
        job_id = str(uuid.uuid4())

        SCHEDULED_JOBS[job_id] = {
            "run_at": run_at,
            "ig_id": ig_id,
            "token": token,
            "url": url,
            "caption": caption,
            "type": mtype
        }

    return "<h3>All posts scheduled. System will auto publish at exact time.</h3>"

# ---------------- TIME WORKER (NO API WASTE) ----------------
def scheduler_worker():
    while True:
        now = datetime.datetime.now()
        for job_id in list(SCHEDULED_JOBS.keys()):
            job = SCHEDULED_JOBS[job_id]
            if now >= job["run_at"]:
                create_container(job_id, job)
                del SCHEDULED_JOBS[job_id]
        time.sleep(10)

# ---------------- CREATE MEDIA (1 API CALL) ----------------
def create_container(job_id, job):
    data = {
        "caption": job["caption"],
        "access_token": job["token"]
    }

    if job["type"] == "image":
        data["image_url"] = job["url"]
    else:
        data["media_type"] = "REELS"
        data["video_url"] = job["url"]

    r = requests.post(
        f"https://graph.facebook.com/v19.0/{job['ig_id']}/media",
        data=data
    ).json()

    if "id" in r:
        PUBLISH_QUEUE[r["id"]] = job
        print("📦 Container Created:", r["id"])
    else:
        print("❌ Create Error:", r)

# ---------------- WEBHOOK VERIFY ----------------
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Invalid"

# ---------------- WEBHOOK CALLBACK (0 POLLING) ----------------
@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.json

    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            if value.get("status") == "FINISHED":
                creation_id = value["id"]
                if creation_id in PUBLISH_QUEUE:
                    publish_media(creation_id, PUBLISH_QUEUE[creation_id])
                    del PUBLISH_QUEUE[creation_id]

    return jsonify({"status": "ok"})

# ---------------- PUBLISH (1 API CALL) ----------------
def publish_media(creation_id, job):
    r = requests.post(
        f"https://graph.facebook.com/v19.0/{job['ig_id']}/media_publish",
        data={
            "creation_id": creation_id,
            "access_token": job["token"]
        }
    ).json()
    print("🚀 Published:", r)

# ---------------- RUN ----------------
threading.Thread(target=scheduler_worker, daemon=True).start()

if __name__ == "__main__":
    app.run(debug=True)
