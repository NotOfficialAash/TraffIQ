import cv2
import threading
import time
import firebase_admin
from firebase_admin import firestore, credentials
import datetime

import random

# Firebase setup
credentials = credentials.Certificate("../firebase-key.json")
firebase_admin.initialize_app(credentials)
db = firestore.client()


# Shared Data + Thread Lock
shared_data = {}
lock = threading.Lock()


def camera_process():
    while True:
        time.sleep(0.2)
        results = {"vehicles": random.randint(1, 20), "accident" : random.choice([True, False])}
        
        with lock:
            shared_data.update(results)
        print("Updated YOLO results: ", results)


def traffic_process():
    while True:
        time.sleep(2)
        with lock:
            data = shared_data.copy()
        print("[Traffic] Read vehicles:", data.get("vehicles"))


def accident_process():
    while True:
        time.sleep(3)
        with lock:
            data = shared_data.copy()
        
        if data.get("accident"):
            print("accident detected")
        else:
            print("No accident")


if __name__ == "__main__":
    try:
        cam_thread = threading.Thread(target=camera_process, daemon=True)
        trf_thread = threading.Thread(target=traffic_process, daemon=True)
        acc_thread = threading.Thread(target=accident_process, daemon=True)

        cam_thread.start()
        trf_thread.start()
        acc_thread.start()

        print("System running. Press Ctrl+C to stop.")

        while True:
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nShutting down cleanly...")