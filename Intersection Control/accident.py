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


def run(shared_data : dict, lock):
    data = None

    while True:
        time.sleep(tick)
        with lock:
            if shared_data != data:
                data = shared_data.copy()

        severity = "major" if data["accident"]["accident_count"] > 1 else "minor"

        if data["accident"]["accident"] == True:
            data_pack = {
                "time" : SERVER_TIMESTAMP,
                "location" : GeoPoint(lat, lng),
                "severity" : severity,
                "ai_conf" : data["accident"]["ai_confidence"],
                "er_informed" : False,
                "er_dispatched" : False
                # , "nearest_hospital" : find_hospital()
            }

            document_id = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S") + f"_{lat}_{lng}"
            database.write_data(collection="accident_data", data=data_pack, document_id=document_id)
            log.info("Auto-Logged Accident Data")

            with lock:
                shared_data["accident"] = {"accident": False, "accident_count": 0, "ai_confidence" : 0}
            