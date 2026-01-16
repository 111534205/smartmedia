from googleapiclient.discovery import build
from config import YOUTUBE_API_KEY
import isodate

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

def get_category_videos(query, category_name, max_results=20):
    # 基礎排除關鍵字
    exclude = " -shorts -short -reels"
    
    # 判斷分類邏輯：電影類需過濾 MV
    if "電影" in category_name:
        q = f"{query} 電影解說 -trailer -MV -music" + exclude
    else:
        q = query + exclude

    # 判斷語言邏輯：中文相關分類使用 zh-Hant，其餘預設為 en
    lang = "zh-Hant" if "中文" in category_name or "日韓" in category_name else "en"

    try:
        search_res = youtube.search().list(
            q=q, part="id", type="video", 
            videoDuration="medium", 
            maxResults=50, 
            relevanceLanguage=lang
        ).execute()
        
        v_ids = [item["id"]["videoId"] for item in search_res.get("items", [])]
        if not v_ids: return []

        details = youtube.videos().list(id=",".join(v_ids), part="snippet,statistics,contentDetails").execute()
        
        videos = []
        for item in details.get("items", []):
            snippet = item["snippet"]
            stats = item.get("statistics", {})
            content = item.get("contentDetails", {})
            
            # 解析影片長度
            dur_raw = isodate.parse_duration(content.get("duration", "PT0S"))
            dur_str = str(dur_raw).split(":")
            
            videos.append({
                "id": item["id"],
                "title": snippet["title"],
                "channel": snippet["channelTitle"],
                "thumb": snippet["thumbnails"]["medium"]["url"],
                "url": f"https://www.youtube.com/watch?v={item['id']}",
                "view_count": int(stats.get("viewCount", 0)),
                "duration": f"{dur_str[-2]}:{dur_str[-1]}" if len(dur_str) >= 2 else "0:00"
            })
        
        # 依觀看次數排序並回傳指定數量
        return sorted(videos, key=lambda x: x['view_count'], reverse=True)[:max_results]
    
    except Exception as e:
        print(f"YouTube API Quota/Error: {e}")
        return []

def search_videos(q):
    try:
        res = youtube.search().list(q=q, part="snippet", type="video", maxResults=20).execute()
        return [{
            "id": i["id"]["videoId"], "title": i["snippet"]["title"],
            "channel": i["snippet"]["channelTitle"], "thumb": i["snippet"]["thumbnails"]["medium"]["url"],
            "url": f"https://www.youtube.com/watch?v={i['id']['videoId']}", "duration": "N/A"
        } for i in res.get("items", []) if "videoId" in i["id"]]
    except:
        return []