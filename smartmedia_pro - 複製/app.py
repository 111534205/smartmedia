from flask import Flask, render_template, request, redirect, session, url_for
from services.youtube_service import get_category_videos, search_videos
from services.analytics import log_click, get_stats, get_hourly_stats, get_advanced_stats, get_custom_videos, add_custom_video, delete_video, update_custom_video
from config import ADMIN_USERNAME, ADMIN_PASSWORD

app = Flask(__name__)
app.secret_key = "smartmedia-2024-secure"

CATEGORIES = [
    ("愛情電影", "romance movie explained"),
    ("動作電影", "action movie explained"),
    ("動畫", "animation movie explained"),
    ("紀錄片", "documentary film"),
    ("中文音樂", "Mandarin music official"),
    ("西方音樂", "Western pop music official"),
    ("日韓音樂", "KPOP JPOP official"),
    ("純音樂", "instrumental music"),
]

@app.route("/")
def index():
    data = {}
    custom_data = get_custom_videos()
    for name, query in CATEGORIES:
        try:
            # 抓取 API 影片
            api_videos = get_category_videos(query, name, max_results=15)
            # 合併該分類的自訂影片
            custom_vids = custom_data.get(name, [])
            data[name] = custom_vids + api_videos
        except Exception as e:
            print(f"API Error for {name}: {e}")
            data[name] = []
    return render_template("index.html", data=data)

@app.route("/search")
def search():
    query = request.args.get("q")
    if not query:
        return redirect(url_for("index"))
    results = search_videos(query)
    return render_template("search_results.html", results=results, query=query)

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        user = request.form.get("username")
        pw = request.form.get("password")
        if user == ADMIN_USERNAME and pw == ADMIN_PASSWORD:
            session["admin"] = True 
            return redirect(url_for("admin"))
        else:
            return render_template("login.html", error="帳號或密碼錯誤")
    return render_template("login.html")

@app.route("/admin")
def admin():
    if not session.get("admin"): 
        return redirect(url_for("admin_login"))
    
    stats = get_stats()           
    hourly = get_hourly_stats()   
    adv = get_advanced_stats()    
    custom_videos = get_custom_videos()
    category_names = [c[0] for c in CATEGORIES]
    
    return render_template(
        "admin.html", 
        stats=stats, 
        hourly=hourly, 
        adv=adv,
        category_names=category_names,
        custom_videos=custom_videos
    )

@app.route("/admin/add_video", methods=["POST"])
def add_video():
    if not session.get("admin"): return redirect(url_for("index"))
    add_custom_video(request.form)
    return redirect(url_for("admin"))

@app.route("/admin/edit_video", methods=["POST"])
def edit_video():
    if not session.get("admin"): return redirect(url_for("index"))
    update_custom_video(request.form)
    return redirect(url_for("admin"))

@app.route("/admin/delete_video/<cat>/<vid>")
def admin_delete_video(cat, vid):
    if not session.get("admin"): return redirect(url_for("index"))
    delete_video(vid, cat)
    return redirect(url_for("admin"))

@app.route("/admin/logout")
def logout():
    session.clear() 
    return redirect(url_for("index"))

@app.route("/click", methods=["POST"])
def click():
    log_click(request.json)
    return "", 204

if __name__ == "__main__":
    app.run(debug=True)