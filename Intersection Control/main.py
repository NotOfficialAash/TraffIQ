import json
import numpy
import threading
import logging as log

import cv2
from ultralytics import YOLO

import traffic
import database
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

def create_region_overlay(frame_shape, regions):
    """
    Creates a transparent overlay with region rectangles and names.
    This avoids redrawing regions every frame.
    """
    overlay = cv2.imread("blank.png") if False else None  # placeholder, not needed
    overlay = 255 * numpy.ones((*frame_shape[:2], 3), dtype=numpy.uint8)  # same size as frame
    overlay[:] = 0  # make it black/transparent

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
    """Blend overlay onto frame with given transparency."""
    return cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)


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

            region_overlay = create_region_overlay(frame.shape, regions)

            frame_id += 1
            skip_frames = 2
            if frame_id % skip_frames != 0:
                capture.grab()
                continue

            try:
                results = model.predict(frame, verbose=False, device=model_device, half=model_half)

            except Exception:
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
                    log.info(f"Vehicles: {shared_data['vehicle']} | Accident: {shared_data['accident']}")
                    prev_data = shared_data.copy()
            
            annotated = results.plot()
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
        log.info("System Starting...  Press Ctrl+C to stop anytime.")
        log.info("Imports Initialized")
        main()
    except KeyboardInterrupt:
        log.info("Safely Shutting Down...")
    except Exception:
        log.exception("Unexpected exception occurred")
