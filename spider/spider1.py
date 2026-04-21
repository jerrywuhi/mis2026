import requests
from bs4 import BeautifulSoup


url = "https://mis2026-zeta.vercel.app/about"
Data = requests.get(url)
Data.endcoding = "utf-8"
#print(Data.text)
sp = BeautifulSoup(Data.text, "html.parser")
result=sp.select("a")


for item in result:
	print(item.txt)
	print(item.get("href"))
	print()
