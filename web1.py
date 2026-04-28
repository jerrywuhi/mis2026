import requests
from bs4 import BeautifulSoup

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

# 判斷是在 Vercel 還是本地
if os.path.exists('serviceAccountKey.json'):
    # 本地環境：讀取檔案
    cred = credentials.Certificate('serviceAccountKey.json')
else:
    # 雲端環境：從環境變數讀取 JSON 字串
    firebase_config = os.getenv('FIREBASE_CONFIG')
    cred_dict = json.loads(firebase_config)
    cred = credentials.Certificate(cred_dict)
    


firebase_admin.initialize_app(cred)



from flask import Flask,render_template, request,jsonify
from datetime import datetime
import random


app = Flask(__name__)


TARGET_URL = 'http://www.atmovies.com.tw/movie/next/'
#電影的網址



def get_atmovies_list():
    movies_list = []
    try:
        # 1. 發送 GET 請求
        response = requests.get(TARGET_URL)
        response.encoding = 'utf-8' # 確保中文不亂碼
        
        if response.status_code == 200:
            # 2. 解析 HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 3. 根據 ATMovies 的結構抓取電影連結
            # ATMovies 的結構通常是 <a href="/movie/.../">電影名稱</a>
            # 他們的電影列表常在某些特定的 table 或 div 裡
            # 這裡我們嘗試抓取所有包含 "/movie/" 的 a 標籤
            
            # 方法一 (較寬鬆): 抓取所有連結包含 /movie/ 且不是首頁的
            for link in soup.find_all('a', href=True):
                href = link['href']
                title = link.get_text(strip=True)
                
                # 過濾：必須是完整的電影連結 (通常長度較長)，且有標題
                if href.startswith('/movie/'):
                    # 組合完整網址
                    full_url = 'http://www.atmovies.com.tw' + href
                    
                    # 避免重複 (例如圖片和標題都連到同一頁)
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
            
            # 方法二 (較精準，需觀察當前網頁結構，通常更有效):
            # 經觀察，ATMmovies 的電影名通常在 class 為 'runtime' 附近的 'a' 標籤
            # 或者在 class 為 'filmTitle' 的 div 內
            
            # 嘗試抓取特定 class (根據網頁結構微調)
            # movies_elements = soup.select('.filmTitle a') # 這是最理想的情況，但網頁結構會變
            # for movie in movies_elements:
            #     # ... 處理方式同上
        
    except Exception as e:
        print(f"爬取發生錯誤: {e}")
        return []

    return movies_list

@app.route("/")
def index():
    link = "<h1>歡迎來到吳冠頡的網站</h1>"
    link +="<a href=/mis>課程</a><hr>"
    link +="<a href=/today>今天日期</a><hr>"
    link +="<a href=/about>網頁</a><hr>"
    link +="<a href=/welcome?u=冠頡&dep=靜宜資管>GET傳值</a><hr>"
    link +="<a href=/account>密碼</a><hr>"
    link += "<a href=/read>讀取Firestore資料(根據lab遞減排序，取前4筆)</a>"
    link += "<a href=/search>查詢老師研究室</a><hr>"
    link += "<a href=/movie_page>電影查詢</a><hr>"
    link += "<br><a href=/movie2>讀取開眼電影即將上映影片，寫入Firestore</a><br>"
    return link    



@app.route('/movie_page')
def movie_page():
    # 這裡會呈現 HTML 頁面
    return render_template('index.html')

@app.route('/get_movies', methods=['GET'])
def search_movies():
    # 獲取前端傳來的關鍵字
    query = request.args.get('query', '').strip().lower()
    
    # 爬取完整列表
    all_movies = get_atmovies_list()
    
    if not query:
        # 如果沒輸入關鍵字，回傳前 10 筆（或全部）
        return jsonify(all_movies[:20])
        
    # **核心搜尋邏輯**：過濾出名稱包含關鍵字的電影
    filtered_movies = []
    for movie in all_movies:
        if query in movie['title'].lower():
            filtered_movies.append(movie)
            
    return jsonify(filtered_movies)

if __name__ == '__main__':
    # 啟動伺服器，預設是 http://127.0.0.1:5000
    app.run(debug=True)



@app.route("/sp1")
def sp1():
    R = ""
    ur1 ="http://127.0.0.1:5000/about" 
    Data = requests.get(ur1)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text,"html.parser")
    result=sp.select("td a")

    for item in result:
        R += item.text + "<br>" + item.get("href") + "<br><br>"
    return R



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
    else:
        return render_template("search.html", results=None)


@app.route("/read")
def read():
    db = firestore.client()
    Temp = ""
    collection_ref = db.collection("靜宜資管")
    docs = collection_ref.order_by("lab",direction=firestore.Query.DESCENDING).limit(3).get()
    for doc in docs:
        Temp += str(doc.to_dict()) + "<br>"


    return Temp



@app.route("/")
def home():
    return "Hello Flask!"

@app.route("/mis")
def course():
    return "<h1>資訊管理導論</h1><a href=/>回到網站首頁</a>"

@app.route("/today")
def today():
    now = datetime.now()
    year  = str(now.year)
    month = str(now.month)
    day   = str(now.day)
    now = year + "年" + month + "月" + day + "日"
    return render_template("today.html", datetime = now)

@app.route("/about")
def about():
    return render_template("mis2a.html")


@app.route("/welcome",methods=["GET"])
def welcome():
    x = request.values.get("u")
    x = request.values.get("dep")
    return render_template("welcome.html",name = x,dep =y)

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        result = "您輸入的帳號是：" + user + "; 密碼為：" + pwd 
        return result
    else:
        return render_template("account.html")

@app.route("/movie2")
def movie2():
  url = "http://www.atmovies.com.tw/movie/next/"
  Data = requests.get(url)
  Data.encoding = "utf-8"
  sp = BeautifulSoup(Data.text, "html.parser")
  result=sp.select(".filmListAllX li")
  lastUpdate = sp.find("div", class_="smaller09").text[5:]

  for item in result:
    picture = item.find("img").get("src").replace(" ", "")
    title = item.find("div", class_="filmtitle").text
    movie_id = item.find("div", class_="filmtitle").find("a").get("href").replace("/", "").replace("movie", "")
    hyperlink = "http://www.atmovies.com.tw" + item.find("div", class_="filmtitle").find("a").get("href")
    show = item.find("div", class_="runtime").text.replace("上映日期：", "")
    show = show.replace("片長：", "")
    show = show.replace("分", "")
    showDate = show[0:10]
    showLength = show[13:]

    doc = {
        "title": title,
        "picture": picture,
        "hyperlink": hyperlink,
        "showDate": showDate,
        "showLength": showLength,
        "lastUpdate": lastUpdate
      }

    db = firestore.client()
    doc_ref = db.collection("電影").document(movie_id)
    doc_ref.set(doc)    
  return "近期上映電影已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate 


if __name__ == "__main__":
    app.run(debug=True)
