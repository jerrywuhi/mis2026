import firebase_admin
from flask import Flask,render_template, request
from datetime import datetime


app = Flask(__name__)


@app.route("/")
def index():
    link = "<h1>歡迎來到吳冠頡的網站</h1>"
    link +="<a href=/mis>課程</a><hr>"
    link +="<a href=/today>今天日期</a><hr>"
    link +="<a href=/about>網頁</a><hr>"
    link +="<a href=/welcome?u=冠頡&dep=靜宜資管>GET傳值</a><hr>"
    link +="<a href=/account>密碼</a><hr>"
    return link    

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




if __name__ == "__main__":
    app.run(debug=True)
