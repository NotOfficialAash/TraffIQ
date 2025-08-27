import json
import numpy
import threading
import logging as log
from sys import exit

import cv2
from ultralytics import YOLO

import traffic
import accident
import database


capture_source = 0
frame_width = 1280
frame_height = 720
lock = threading.Lock()
model = YOLO(model="custom_yolo.pt", verbose=False)
model_device = 'cpu'
model_half = False
regions = json.load(open("regions.json"))

log.basicConfig(
    level=log.INFO,
    format="%(asctime)s // [%(levelname)s] %(message)s"
)

shared_data = {
    "vehicle": {region : 0 for region in regions.keys()},
    "total" : 0,
    "accident": {"accident": False, "accident_count": 0}
}


def capture_init():
    capture = cv2.VideoCapture(capture_source)
    if not capture.isOpened():
        log.critical("Unable to Open Capture Source")
        exit(1)
    
    capture.release()


def get_region(cx, cy):
    for name, (rx1, ry1, rx2, ry2) in regions.items():
        if rx1 <= cx <= rx2 and ry1 <= cy <= ry2:
            return name
    return None


def create_region_overlay(frame_shape, regions):
    overlay = numpy.zeros((*frame_shape[:2], 3), dtype=numpy.uint8)  # fully transparent

    for name, (rx1, ry1, rx2, ry2) in regions.items():
        # Draw rectangle
        cv2.rectangle(overlay, (rx1, ry1), (rx2, ry2), (0, 255, 0), 2)
        # Draw label
        cv2.putText(
            overlay, name, (rx1, ry1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2
        )
    return overlay


def blend_overlay(frame, overlay, alpha=0.5):
    return cv2.addWeighted(frame, 1, overlay, alpha, 0)


def main():
    log.info("Initializing and Starting Threads...")
    trf_thread = threading.Thread(target=traffic.run, args=(shared_data, lock), daemon=True)
    acc_thread = threading.Thread(target=accident.run, args=(shared_data, lock), daemon=True)
    trf_thread.start()
    acc_thread.start()
    log.info("Threads Started")

    capture = cv2.VideoCapture(capture_source)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

    log.info("Capture Source Open")
    names = model.names

    dummy_frame = numpy.zeros((frame_height, frame_width, 3), dtype=numpy.uint8)
    region_overlay = create_region_overlay(dummy_frame.shape, regions)


    try:
        frame_id = 0
        prev_data = None

        while capture.isOpened():
            success, frame = capture.read()
            if not success:
                log.error("Failed to read frame")
                break

            frame_id += 1
            skip_frames = 2
            if frame_id % skip_frames != 0:
                continue

            try:
                results = model.predict(frame, verbose=False, device=model_device, half=model_half)

            except Exception:
                log.exception("Model Inference Failed, Skipping Frame")
                continue

            result = results[0]

            accident_count = 0
            total_vehicle_count = 0
            region_counts = dict.fromkeys(regions.keys(), 0)

            for box, classid in zip(result.boxes.xyxy.cpu().numpy(), result.boxes.cls.cpu().numpy()):
                x1, y1, x2, y2 = box.astype(int)
                label = names[int(classid)]

                if label == "accident":
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

                if shared_data != prev_data:
                    log.info(f"Vehicles: {shared_data['vehicle']} | Accident: {shared_data['accident']}")
                    prev_data = shared_data.copy()
            
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
        log.info("Systems  Starting...")
        capture_init()
        traffic.init()
        database.init()
        log.info("Systems Initialized")
        main()

    except KeyboardInterrupt:
        log.critical("User Commanded Immediate Shut Down")
        
    except Exception:
        log.exception("Unexpected exception occurred")

    finally:
        traffic.close_arduino()
        log.info("Safely Shutting Down...")
