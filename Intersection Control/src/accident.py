"""
================================================================================
Project: Smart Traffic and Accident Monitoring System
File: accident.py
Author(s): Aashrith Srinivasa.
License: See LICENSE file in the repository for full terms.
Description:
    Monitors accident events from shared data, logs accident information
    including severity and AI confidence to Firestore, and resets
    accident status after logging.
================================================================================
"""

# TODO: Implement algorithm to find nearest hospital
# TODO: Log nearest hospital along with accident info

import time
import datetime
import logging as log

from firebase_admin.firestore import GeoPoint, SERVER_TIMESTAMP

import database


lat, lng = 12.312735, 76.583278
tick = 0.1


active_accident = False
last_no_accident_time = time.time()
gap_time = 5  # seconds of "no accident" needed before logging a new one

def run(shared_data: dict, lock):
    global active_accident, last_no_accident_time
    data = None

    while True:
        time.sleep(tick)
        with lock:
            if shared_data != data:
                data = shared_data.copy()

        severity = "major" if data["accident"]["accident_count"] > 1 else "minor"

        if data["accident"]["accident"]:
            if not active_accident:
                # First time we see accident → log it
                data_pack = {
                    "time": SERVER_TIMESTAMP,
                    "location": GeoPoint(lat, lng),
                    "severity": severity,
                    "ai_conf": data["accident"]["ai_confidence"],
                    "er_informed": False,
                    "er_dispatched": False,
                    "real": data["accident"]["ai_confidence"] > 25
                }

                document_id = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S") + f"_{lat}_{lng}"
                database.write_data("accident_data", data_pack, document_id)
                log.info("Auto-Logged Accident Data")

                active_accident = True
        else:
            # Accident not detected → reset after some time
            if active_accident:
                last_no_accident_time = time.time()
                active_accident = False