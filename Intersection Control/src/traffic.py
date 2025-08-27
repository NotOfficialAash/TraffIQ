"""
================================================================================
Project: Smart Traffic and Accident Monitoring System
File: traffic.py
Author(s): Aashrith Srinivasa.
License: See LICENSE file in the repository for full terms.
Description:
    Handles traffic light control, vehicle counting per region, and
    logging traffic density data to Firestore at regular intervals.
================================================================================
"""


import time
import datetime
import logging as log
from sys import exit
from json import load

import serial
from firebase_admin.firestore import GeoPoint, SERVER_TIMESTAMP

import database


tick = 0.1
arduino = None
log_interval = 1800
lat, lng = 12.312735, 76.583278
regions = load(open("../regions.json"))
region_names = list(regions.keys())
signal_order = {
    region_names[i]: region_names[(i + 1) % len(region_names)]
    for i in range(len(region_names))
}

PHASE_FLOW = {
    "green": "yellow_stop",
    "yellow_stop": "yellow_start",
    "yellow_start": "green"
}


def init():
    global arduino
    try:
        arduino = serial.Serial(port="COM6", baudrate=9600, timeout=1)
    except serial.SerialException as e:
        log.critical(f"Arduino connection failed: {e}")
        exit(2)


def send_signal(cmd: str):
    try:
        arduino.write((cmd + "\n").encode())
        time.sleep(0.05)
    except serial.SerialException as e:
        log.error(f"Arduino write failed: {e}")


def set_signal_state(signal: str, red: bool, yellow: bool, green: bool):
    send_signal(f"{signal}_R_{'ON' if red else 'OFF'}")
    send_signal(f"{signal}_Y_{'ON' if yellow else 'OFF'}")
    send_signal(f"{signal}_G_{'ON' if green else 'OFF'}")
    log.info(f"{signal} → {'R' if red else ''}{'Y' if yellow else ''}{'G' if green else ''}")


def close_arduino():
    send_signal("EXIT")
    arduino.close()
    log.info("Arduino Connection Closed.")


def get_durations(vehicle_counts):
    base = {"yellow_stop": 2, "yellow_start": 2}
    for region, count in vehicle_counts.items():
        base[f"green_{region}"] = 9 if count > 1 else 4
    return base


def run(shared_data : dict, lock):
    current_green = region_names[0]
    next_green = signal_order[current_green]
    current_phase = "green"
    last_switch_time = time.time()
    last_log_time = time.time()

    set_signal_state(current_green, red=False, yellow=False, green=True)

    durations = get_durations(shared_data.get("vehicle", {}))
    phase_durations = {
        "green": durations.get(f"green_{current_green}", 4),
        "yellow_stop": durations["yellow_stop"],
        "yellow_start": durations["yellow_start"]
    }

    while True:
        time.sleep(tick)
        current_time = time.time()
        elapsed_time = current_time - last_switch_time

        if elapsed_time >= phase_durations[current_phase]:
            with lock:
                data = shared_data.copy()

            durations = get_durations(data.get("vehicle", {}))

        phase_durations = {
            "green": durations.get(f"green_{current_green}", 4),
            "yellow_stop": durations["yellow_stop"],
            "yellow_start": durations["yellow_start"]
        }

        if elapsed_time >= phase_durations[current_phase]:
            if current_phase == "green":
                set_signal_state(current_green, red=False, yellow=True, green=False)

            elif current_phase == "yellow_stop":
                set_signal_state(current_green, red=True, yellow=False, green=False)
                set_signal_state(next_green, red=False, yellow=True, green=False)

            elif current_phase == "yellow_start":
                set_signal_state(next_green, red=False, yellow=False, green=True)
                current_green = next_green
                next_green = signal_order[current_green]

            current_phase = PHASE_FLOW[current_phase]
            last_switch_time = current_time

        if current_time - last_log_time >= log_interval:
            data_pack = {
                "time": SERVER_TIMESTAMP,
                "location" : GeoPoint(lat, lng),
                "density" : data["total"]
                }

            document_id = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            database.write_data(collection="traffic_data", data=data_pack, document_id=document_id)
            last_log_time = current_time
            log.info("Auto-Logged Traffic Density Data")
