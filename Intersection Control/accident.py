import datetime
import logging as log

import database


lat, lng = 12.312735, 76.583278

def run(shared_data : dict, lock):
    prev_data = None

    with lock:
        if shared_data != prev_data:
            prev_data = shared_data.copy()

    severity = "major" if prev_data["accident"]["accident_count"] > 1 else "minor"

    if prev_data["accident"]["accident"] == True:
        accident_data = {
            "time" : datetime.datetime.now(),
            "location" : {"lat" : lat, "lng" : lng},
            "severity" : severity,
            "ai_conf" : 0,
            "er_informed" : False,
            "er_dispatched" : False
        }
