import threading
import logging as log
import json

import cv2
from ultralytics import YOLO

import database
import traffic
import accident


camera_source = 0
lock = threading.Lock()
model = YOLO(model="custom_yolo.pt", verbose=False)
model_device = 'cpu'
model_half = False
regions = json.load(open("regions.json"))

log.basicConfig(
    level=log.INFO,
    format="%(asctime)s // [MAIN::%(levelname)s] %(message)s"
)

shared_data = {
    "vehicle": {region : 0 for region in regions.keys()},
    "accident": {"accident": False, "accidentCount": 0}
}


def get_region(cx, cy):
    for name, (rx1, ry1, rx2, ry2) in regions.items():
        if rx1 <= cx <= rx2 and ry1 <= cy <= ry2:
            return name
    return None


def main():
    log.info("Initializing and Starting Threads...")
    trf_thread = threading.Thread(target=..., daemon=True)
    acc_thread = threading.Thread(target=..., daemon=True)
    dbs_thread = threading.Thread(target=..., daemon=True)
    trf_thread.start()
    acc_thread.start()
    dbs_thread.start()
    log.info("Threads Started")

    capture = cv2.VideoCapture(camera_source)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not capture.isOpened():
        log.critical("Unable to Open Capture Source")
        return

    log.info("Capture Source Open")
    names = model.names

    try:
        frame_id = 0
        prev_data = None

        while capture.isOpened():
            success, frame = capture.read()
            if not success:
                log.error("Failed to read frame")
                break

            frame_id += 1
            process_every = 2
            if frame_id % process_every != 0:
                capture.grab()
                continue

            try:
                results = model.predict(frame, verbose=False, device=model_device, half=model_half)
            except:
                log.exception("Model Inference Failed, Skipping Frame")
                continue

            result = results[0]

            accident_count = 0
            region_counts = dict.fromkeys(regions.keys(), 0)

            for box, classid in zip(result.boxes.xyxy.cpu().numpy(), result.boxes.cls.cpu().numpy()):
                x1, y1, x2, y2 = box.astype(int)
                label = names[int(classid)]

                if label == "accident":
                    accident_count += 1

                elif label == "objects":
                    cx = (x1 + x2) // 2
                    cy = (y1 + y2) // 2
                    region = get_region(cx, cy)
                    if region:
                        region_counts[region] += 1

            with lock:
                shared_data["vehicle"] = region_counts.copy()
                shared_data["accident"]["accident"] = accident_count > 0
                shared_data["accident"]["accidentCount"] = accident_count

                if shared_data != prev_data:
                    log.info(shared_data)
                    prev_data = shared_data.copy()

    except Exception:
        log.exception("Unexpected exception occurred")

    finally:
        capture.release()
        cv2.destroyAllWindows()
        log.info("Capture Released and Resources Cleaned")



if __name__ == "__main__":
    try:
        log.info("System Starting...  Press Ctrl+C to stop anytime.")
        log.info("Imports Initialized")
        main()
    except KeyboardInterrupt:
        log.info("Safely Shutting Down...")
    except Exception:
        log.exception("Unexpected exception occurred")
