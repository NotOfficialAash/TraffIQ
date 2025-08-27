"""
================================================================================
Project: Smart Traffic and Accident Monitoring System
File: database.py
Author(s): 
    - Aashrith Srinivasa.
    - Atrey K Urs (Databse Initialization).
License: See LICENSE file in the repository for full terms.
Description:
    Provides Firestore initialization and helper functions to write and 
    update documents in collections. Handles error logging for database
    operations.
================================================================================
"""


from sys import exit
import logging as log

import firebase_admin
import google.auth.exceptions
import google.api_core.exceptions
from firebase_admin import firestore, exceptions as fb_exceptions


file_path = "firebase-key.json"


def init():
    global database
    try: 
        if not firebase_admin._apps:
            credential = firebase_admin.credentials.Certificate(file_path)
            firebase_admin.initialize_app(credential=credential)
            database = firestore.client()

    except FileNotFoundError:
        log.critical(f"Firebase key file not found at '{file_path}'.")
        exit(3)

    except ValueError as e:
        log.critical(f"Invalid Firebase key format: {e}")
        exit(3)

    except google.auth.exceptions.DefaultCredentialsError as e:
        log.critical(f"Invalid or expired credentials: {e}")
        exit(3)

    except fb_exceptions.FirebaseError as e:
        log.critical(f"Firebase Admin SDK error: {e}")
        exit(3)

    except google.api_core.exceptions.GoogleAPIError as e:
        log.critical(f"Firestore API error (network or quota issue): {e}")
        exit(3)

    except Exception as e:
        log.critical(f"Unexpected exception during Firestore init: {e}")
        exit(3)
    

def write_data(collection : str, document_id : str, data : dict):
    try:
        doc_ref = database.collection(collection).document(document_id)
        doc_ref.set(data)
        log.info(f"Wrote data to {collection}/{doc_ref.id}")
    
    except google.api_core.exceptions.GoogleAPIError as e:
        log.error(f"Firestore API error during write: {e}")

    except Exception as e:
        log.error(f"Failed to write to {collection}/{document_id}: {e}")


def update_data(collection: str, document_id : str, data : dict):
    try:
        doc_ref = database.collection(collection).document(document_id)
        doc_ref.update(data)
        log.info(f"Updated {collection}/{document_id} with {data}")

    except google.api_core.exceptions.NotFound:
        log.error(f"Document {collection}/{document_id} not found.")

    except google.api_core.exceptions.GoogleAPIError as e:
        log.error(f"Firestore API error during update: {e}")
        
    except Exception as e:
        log.error(f"Failed to update {collection}/{document_id}: {e}")
