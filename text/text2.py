import requests
city = "臺中市"
token = "rdec-key-123-45678-011121314"
url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=" + token + "&format=JSON&locationName=" + str(city)
Data = requests.get(url)
print(Data.text)
