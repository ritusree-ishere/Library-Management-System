import firebase_admin  # type: ignore[reportMissingImports]
from firebase_admin import credentials, firestore  # type: ignore[reportMissingImports]

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()