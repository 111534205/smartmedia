import json, os
from datetime import datetime

ANALYTICS_FILE = "data/analytics.json"
CUSTOM_FILE = "data/custom_videos.json"

def _load(path, default):
    if not os.path.exists(path): return default
    with open(path, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except: return default

def _save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def log_click(data):
    logs = _load(ANALYTICS_FILE, [])
    logs.append({"video": data, "time": datetime.now().isoformat()})
    _save(ANALYTICS_FILE, logs)

def get_stats(): return _load(ANALYTICS_FILE, [])

def get_hourly_stats():
    logs = get_stats()
    hourly = {f"{i:02d}-{(i+2):02d}": 0 for i in range(0, 24, 2)}
    for l in logs:
        if isinstance(l, dict):
            hr = datetime.fromisoformat(l['time']).hour
            slot = f"{(hr//2)*2:02d}-{(hr//2)*2+2:02d}"
            hourly[slot] += 1
    return hourly

def get_advanced_stats():
    logs = get_stats()
    ranking = {}
    for l in logs:
        if isinstance(l, dict):
            title = l.get("video", {}).get("title", "未知")
            ranking[title] = ranking.get(title, 0) + 1
    return {
        "total": len(logs),
        "top": sorted(ranking.items(), key=lambda x: x[1], reverse=True)[:5]
    }

def get_custom_videos(): return _load(CUSTOM_FILE, {})

def add_custom_video(form):
    data = get_custom_videos()
    cat = form.get("category")
    if cat not in data: data[cat] = []
    
    url = form.get("url")
    vid = url.split("v=")[-1].split("&")[0] if "v=" in url else url.split("/")[-1]
    
    data[cat].append({
        "id": vid, "title": form.get("title"), "channel": "管理員",
        "thumb": f"https://img.youtube.com/vi/{vid}/mqdefault.jpg",
        "url": url, "view_count": 999999, "year": "2024", "duration": "自訂"
    })
    _save(CUSTOM_FILE, data)

def update_custom_video(form):
    data = get_custom_videos()
    cat = form.get("category")
    vid = form.get("old_id")
    if cat in data:
        for v in data[cat]:
            if v['id'] == vid:
                v['title'] = form.get("title")
                v['url'] = form.get("url")
                # 更新 ID 與 縮圖
                new_url = form.get("url")
                new_id = new_url.split("v=")[-1].split("&")[0] if "v=" in new_url else new_url.split("/")[-1]
                v['id'] = new_id
                v['thumb'] = f"https://img.youtube.com/vi/{new_id}/mqdefault.jpg"
                break
        _save(CUSTOM_FILE, data)

def delete_video(vid, cat):
    data = get_custom_videos()
    if cat in data:
        data[cat] = [v for v in data[cat] if v['id'] != vid]
        _save(CUSTOM_FILE, data)