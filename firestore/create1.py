import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

doc = {
  "name": "吳冠頡",
  "mail": "wu0952686160@gmail.com",
  "lab": 579
}

doc_ref = db.collection("靜宜資管2026a").document("tcyang")
doc_ref.set(doc)
