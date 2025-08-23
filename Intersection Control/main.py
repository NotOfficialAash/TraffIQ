import cv2
import threading
import time
import firebase_admin
from firebase_admin import firestore, credentials
import datetime
import logging as log
from ultralytics import YOLO

import random

# Firebase setup
credentials = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(credentials)
db = firestore.client()


# Shared Data + Thread Lock
shared_data = {}
lock = threading.Lock()


# Global Variables
cam_src = 1
model = YOLO("custom_yolo.pt")
log.basicConfig(
    level=log.INFO,  # set minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s // [%(levelname)s] %(message)s"
)


def yolo_process():
    capture = cv2.VideoCapture(cam_src)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not capture.isOpened():
        log.error("Unable to Open Capture Source")
        return
    
    log.info("Capture Source Opened")

    try:
        while capture.isOpened():
            success, frames = capture.read()
            if not success:
                log.error("Video Stream Not Found")
                return

            results = model(frames)[0]

            annotated = results.plot()
            cv2.imshow("Live", annotated)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:  
        log.critical(e)


def traffic_process():
    while True:
        time.sleep(2)
        with lock:
            data = shared_data.copy()
        # print("[Traffic] Read vehicles:", data.get("vehicles"))


def accident_process():
    while True:
        time.sleep(3)
        with lock:
            data = shared_data.copy()
        
        # if data.get("accident"):
        #     print("accident detected")
        # else:
        #     print("No accident")


if __name__ == "__main__":
    try:
        cam_thread = threading.Thread(target=yolo_process, daemon=True)
        trf_thread = threading.Thread(target=traffic_process, daemon=True)
        acc_thread = threading.Thread(target=accident_process, daemon=True)

        cam_thread.start()
        trf_thread.start()
        acc_thread.start()

        log.info("System running. Press Ctrl+C to stop.")

        while True:
            time.sleep(0.1)

    except KeyboardInterrupt:
        log.info("Shutting down cleanly...")