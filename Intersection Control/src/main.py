"""
================================================================================
Project: Smart Traffic and Accident Monitoring System
File: main.py
Author(s):
    - Aashrith Srinivasa.
    - Punya S (Training YOLO on custom dataset).
    - Atrey K Urs (Training YOLO on custom dataset).
License: See LICENSE file in the repository for full terms.
Description:
    Entry point for the traffic and accident monitoring system. 
    Initializes threads, YOLO model, video capture, and coordinates 
    traffic light control and accident detection.
================================================================================
"""



import threading
import logging as log
from sys import exit

import cv2
import numpy
from ultralytics import YOLO

import traffic
import accident
import database
import webserver


capture_source = 0
frame_width = 1280
frame_height = 720
lock = threading.Lock()
model = YOLO(model="../custom_yolo.pt", verbose=False)
model_device = 'cpu'
model_half = False

log.basicConfig(
    level=log.INFO,
    format="%(asctime)s // %(levelname)s [%(filename)s] :: %(message)s"
)


def capture_init():
    capture = cv2.VideoCapture(capture_source)
    if not capture.isOpened():
        log.critical("Unable to Open Capture Source")
        exit(1)
    
    capture.release()


def get_region(cx, cy):
    point = (float(cx), float(cy))   # force tuple of floats
    for name, points in regions.items():
        contour = numpy.array(points, dtype=numpy.int32)
        if cv2.pointPolygonTest(contour, point, False) >= 0:
            return name
    return None


def create_region_overlay(frame_shape, regions):
    overlay = numpy.zeros((*frame_shape[:2], 3), dtype=numpy.uint8)

    for name, points in regions.items():
        pts = numpy.array(points, numpy.int32).reshape((-1, 1, 2))

        # Transparent fill (light green)
        cv2.fillPoly(overlay, [pts], (0, 255, 0))

        # Outline
        cv2.polylines(overlay, [pts], isClosed=True, color=(0, 0, 0), thickness=2)

        # Label
        x, y = points[0]
        cv2.putText(
            overlay, name, (x, y - 5),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2
        )

    return overlay


def blend_overlay(frame, overlay, alpha=0.5):
    return cv2.addWeighted(frame, 1, overlay, alpha, 0)


def main():
    log.info("Starting Threads...")
    trf_thread = threading.Thread(target=traffic.run, args=(shared_data, lock), daemon=True)
    acc_thread = threading.Thread(target=accident.run, args=(shared_data, lock), daemon=True)
    wsk_thread = threading.Thread(target=webserver.run, args=("0.0.0.0", 8765), daemon=True)
    trf_thread.start()
    acc_thread.start()
    wsk_thread.start()
    log.info("Threads Started")

    capture = cv2.VideoCapture(capture_source, cv2.CAP_DSHOW)
    capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
    log.info("Capture Source Open")

    names = model.names
    dummy_frame = numpy.zeros((frame_height, frame_width, 3), dtype=numpy.uint8)
    region_overlay = create_region_overlay(dummy_frame.shape, regions)


    try:
        prev_data = None

        while capture.isOpened():
            success, frame = capture.read()
            if not success:
                log.error("Failed to read frame")
                break

            try:
                results = model.predict(frame, verbose=False, device=model_device, half=model_half)

            except Exception:
                log.exception("Model Inference Failed, Skipping Frame")
                continue

            result = results[0]

            confidence = 0
            accident_count = 0
            total_vehicle_count = 0
            region_counts = dict.fromkeys(regions.keys(), 0)

            for box, classid, conf in zip(result.boxes.xyxy.cpu().numpy(), result.boxes.cls.cpu().numpy(), result.boxes.conf.cpu().numpy()):
                x1, y1, x2, y2 = box.astype(int)
                label = names[int(classid)]

                if label == "accident":
                    confidence = float(conf) * 100
                    accident_count += 1

                elif label == "objects":
                    total_vehicle_count += 1
                    cx = (x1 + x2) // 2
                    cy = (y1 + y2) // 2
                    region = get_region(cx, cy)
                    if region:
                        region_counts[region] += 1

            with lock:
                shared_data["vehicle"] = region_counts.copy()
                shared_data["total"] = total_vehicle_count
                shared_data["accident"]["accident"] = accident_count > 0
                shared_data["accident"]["accident_count"] = accident_count
                shared_data["accident"]["ai_confidence"] = confidence

                if shared_data != prev_data:
                    # log.info(f"Vehicles: {shared_data['vehicle']} | Accident: {shared_data['accident']}")
                    prev_data = shared_data.copy()
            
            webserver.latest_frame = frame.copy()

            annotated = result.plot()
            annotated = blend_overlay(annotated, region_overlay, alpha=0.5)
            cv2.imshow("Live", annotated)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                return

    except Exception:
        log.exception("Unexpected exception occurred")

    finally:
        capture.release()
        cv2.destroyAllWindows()
        log.info("Capture Released and Resources Cleaned")


if __name__ == "__main__":
    try:
        log.info("Starting Systems and Initializing...")

        capture_init()
        traffic.init()
        database.init()

        regions = database.get_intersection_data()

        shared_data = {
            "vehicle": {region : 0 for region in regions.keys()},
            "total" : 0,
            "accident": {"accident": False, "accident_count": 0, "ai_confidence" : 0}
        }
        
        log.info("Systems Initialized")
        main()

    except KeyboardInterrupt:
        log.critical("User Commanded Immediate Shut Down")

    except Exception:
        log.exception("Unexpected exception occurred")

    finally:
        traffic.close_arduino()
        log.info("Safely Shutting Down...")
