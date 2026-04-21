import requests
from bs4 import BeautifulSoup


url = "https://mis2026-zeta.vercel.app/about"
Data = requests.get(url)
Data.endcoding = "utf-8"
#print(Data.text)
sp = BeautifulSoup(Data.text, "html.parser")
result=sp.find(id="h2text")



print(result)
