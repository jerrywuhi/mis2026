import os
import json
import random
import requests
from datetime import datetime
from bs4 import BeautifulSoup

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from flask import Flask, render_template, request, jsonify

# --- 1. 初始化 Firebase ---
if os.path.exists('serviceAccountKey.json'):
    # 本地環境
    cred = credentials.Certificate('serviceAccountKey.json')
else:
    # 雲端環境
    firebase_config = os.getenv('FIREBASE_CONFIG')
    if firebase_config:
        cred_dict = json.loads(firebase_config)
        cred = credentials.Certificate(cred_dict)
    else:
        # 若都沒有配置，視情況處理或拋出錯誤
        cred = None

if cred and not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# --- 2. Flask App 設定 ---
app = Flask(__name__)
TARGET_URL = 'http://www.atmovies.com.tw/movie/next/'

# --- 3. 輔助函式 (爬蟲邏輯) ---
def get_atmovies_list():
    movies_list = []
    try:
        response = requests.get(TARGET_URL)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                title = link.get_text(strip=True)
                if href.startswith('/movie/'):
                    full_url = 'http://www.atmovies.com.tw' + href
                    is_duplicate = False
                    for existing_movie in movies_list:
                        if existing_movie['url'] == full_url:
                            is_duplicate = True
                            break
                    if not is_duplicate and len(title) > 0 and 'index.html' not in href:
                         movies_list.append({
                            'title': title,
                            'url': full_url
                        })
    except Exception as e:
        print(f"爬取發生錯誤: {e}")
        return []
    return movies_list

# --- 4. 路由定義 ---

@app.route("/")
def index():
    # 保留原本首頁內容與超連結
    link = "<h1>歡迎來到吳冠頡的網站</h1>"
    link += "<a href=/mis>課程</a><hr>"
    link += "<a href=/today>今天日期</a><hr>"
    link += "<a href=/about>網頁</a><hr>"
    link += "<a href=/welcome?u=冠頡&dep=靜宜資管>GET傳值</a><hr>"
    link += "<a href=/account>密碼</a><hr>"
    link += "<a href=/read>讀取Firestore資料(根據lab遞減排序，取前4筆)</a><hr>"
    link += "<a href=/search>查詢老師研究室</a><hr>"
    link += "<a href=/movie_page>電影查詢</a><hr>"
    link += "<br><a href=/movie2>讀取開眼電影即將上映影片，寫入Firestore</a><br>"
    link += "<a href=/movie_search>電影資料庫查詢</a><hr>"
    return link


@app.route('/movie_search')
def movie_search():
    # 這會開啟上面那個 HTML 頁面
    return render_template('movie_search.html')


@app.route("/search_woman")
def search_woman():
    info = ""
    db = firestore.client()  
    docs = db.collection("電影").get() 
    for doc in docs:
        movie_data = doc.to_dict()
        if "女" in movie_data.get("title", ""):
            info += "片名：" + movie_data.get("title", "") + "<br>" 
            info += "海報：" + movie_data.get("picture", "") + "<br>"
            info += "影片介紹：" + movie_data.get("hyperlink", "") + "<br>"
            info += "片長：" + movie_data.get("showLength", "") + " 分鐘<br>" 
            info += "上映日期：" + movie_data.get("showDate", "") + "<br><br>"           
    if not info:
        return "目前資料庫中沒有片名包含「女」的電影。<br><a href=/>回到首頁</a>"
    return info


@app.route("/mis")
def course():
    return "<h1>資訊管理導論</h1><a href=/>回到網站首頁</a>"

@app.route("/today")
def today():
    now = datetime.now()
    now_str = now.strftime("%Y年%m月%d日")
    return render_template("today.html", datetime=now_str)

@app.route("/about")
def about():
    return render_template("mis2a.html")

@app.route("/welcome", methods=["GET"])
def welcome():
    user_name = request.values.get("u")
    department = request.values.get("dep")
    # 修正原本程式中 y 未定義的問題
    return render_template("welcome.html", name=user_name, dep=department)

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        return f"您輸入的帳號是：{user}; 密碼為：{pwd}"
    return render_template("account.html")

@app.route('/movie_page')
def movie_page():
    return render_template('index.html')

@app.route('/get_movies', methods=['GET'])
def search_movies():
    query = request.args.get('query', '').strip().lower()
    all_movies = get_atmovies_list()
    if not query:
        return jsonify(all_movies[:20])
    filtered_movies = [m for m in all_movies if query in m['title'].lower()]
    return jsonify(filtered_movies)

@app.route("/read")
def read():
    db = firestore.client()
    temp = ""
    collection_ref = db.collection("靜宜資管")
    # 依照原本邏輯：根據lab遞減排序，取前 3 筆 (首頁文字寫 4，但程式寫 limit(3))
    docs = collection_ref.order_by("lab", direction=firestore.Query.DESCENDING).limit(3).get()
    for doc in docs:
        temp += str(doc.to_dict()) + "<br>"
    return temp

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        keyword = request.form["keyword"]
        db = firestore.client()
        collection_ref = db.collection("靜宜資管")
        docs = collection_ref.get()
        results = []
        for doc in docs:
            user = doc.to_dict()
            if keyword in user.get("name", ""):
                results.append(f"{user['name']}老師的研究室是在{user['lab']}")
        return render_template("search.html", results=results, keyword=keyword)
    return render_template("search.html", results=None)

@app.route("/movie2")
def movie2():
    url = "http://www.atmovies.com.tw/movie/next/"
    data = requests.get(url)
    data.encoding = "utf-8"
    soup = BeautifulSoup(data.text, "html.parser")
    result = soup.select(".filmListAllX li")
    # 取得更新日期
    try:
        lastUpdate = soup.find("div", class_="smaller09").text[5:]
    except:
        lastUpdate = "未知"

    db = firestore.client()
    for item in result:
        try:
            picture = item.find("img").get("src").replace(" ", "")
            title_tag = item.find("div", class_="filmtitle")
            title = title_tag.text
            href = title_tag.find("a").get("href")
            movie_id = href.replace("/", "").replace("movie", "")
            hyperlink = "http://www.atmovies.com.tw" + href
            
            show_text = item.find("div", class_="runtime").text.replace("上映日期：", "").replace("片長：", "").replace("分", "")
            showDate = show_text[0:10]
            showLength = show_text[13:].strip()

            doc = {
                "title": title,
                "picture": picture,
                "hyperlink": hyperlink,
                "showDate": showDate,
                "showLength": showLength,
                "lastUpdate": lastUpdate
            }
            db.collection("電影").document(movie_id).set(doc)
        except Exception:
            continue
            
    return "近期上映電影已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate

@app.route("/sp1")
def sp1():
    # 此路由依賴本地運行中的 about 頁面
    r_content = ""
    local_url = "http://127.0.0.1:5000/about" 
    try:
        data = requests.get(local_url)
        data.encoding = "utf-8"
        soup = BeautifulSoup(data.text, "html.parser")
        result = soup.select("td a")
        for item in result:
            r_content += item.text + "<br>" + item.get("href") + "<br><br>"
    except:
        r_content = "無法讀取本地 URL，請確保伺服器已啟動。"
    return r_content
# 建議將 db 初始化放在外面



# --- 5. 啟動區塊 (必須放在最後) ---
if __name__ == '__main__':
    app.run(debug=True)