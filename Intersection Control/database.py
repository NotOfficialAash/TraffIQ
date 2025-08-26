'''
    Import required libraries.
        Import firestore SEPARATELY. You can't access firestore from the first import statement.
'''
import firebase_admin
from firebase_admin import firestore

'''
    Create a 'credentials certificate' using the keys provided in the JSON file.
    Pass the 'certificate' object to initialize the database application.
    Create a firestore client object.
'''
credential = firebase_admin.credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(credential=credential)

database = firestore.client()