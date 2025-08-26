def yolo_process():
            with lock:
                shared_data["accidents"] = accident_count
                shared_data["regions"] = region_counts

            log.info(f"Accidents: {accident_count}, Region Counts: {region_counts}")

            # Draw regions
            for (rx1, ry1, rx2, ry2) in regions.values():
                cv2.rectangle(frames, (rx1, ry1), (rx2, ry2), (0, 255, 0), 2)


            annotated = results.plot()
            cv2.imshow("Live", annotated)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                return

def traffic_process():
    signal_order = {"region1": "region2", "region2": "region3", "region3": "region1"}
    current_green = "region1"
    next_green = signal_order[current_green]
    current_phase = "green"
    last_sent_second = -1
    last_switch_time = time.time()

    def log_signal_state(region, red, yellow, green):
        log.info(f"{region.upper()} => R:{red} Y:{yellow} G:{green}")

    # initial state
    log_signal_state("region1", red=False, yellow=False, green=True)
    log_signal_state("region2", red=True, yellow=False, green=False)
    log_signal_state("region3", red=True, yellow=False, green=False)

    while True:
        time.sleep(1)  # main traffic loop tick

        with lock:
            data = shared_data.copy()
        region_counts = data.get("regions", {})

        traffic_count_A = region_counts.get("region1", 0)
        traffic_count_B = region_counts.get("region2", 0)
        traffic_count_C = region_counts.get("region3", 0)

        # dynamic green times
        duration_A = 9 if traffic_count_A > 1 else 4
        duration_B = 9 if traffic_count_B > 1 else 4
        duration_C = 9 if traffic_count_C > 1 else 4
        duration_yellow_stop = 2
        duration_yellow_start = 2

        if current_green == "region1":
            duration_active = duration_A
        elif current_green == "region2":
            duration_active = duration_B
        else:
            duration_active = duration_C

        # --- Timing logic ---
        current_time = time.time()
        elapsed_time = current_time - last_switch_time
        current_second = int(elapsed_time)

        if current_second != last_sent_second:
            last_sent_second = current_second
            if current_phase == "green":
                remaining = max(0, duration_active - current_second)
                log.info(f"GREEN {current_green.upper()} - {remaining}s left")
            elif current_phase == "yellow_stop":
                remaining = max(0, duration_yellow_stop - current_second)
                log.info(f"YELLOW STOP {current_green.upper()} - {remaining}s left")
            elif current_phase == "yellow_start":
                remaining = max(0, duration_yellow_start - current_second)
                log.info(f"YELLOW START {next_green.upper()} - {remaining}s left")

        # --- Phase switching ---
        if current_phase == "green":
            if elapsed_time >= duration_active:
                log_signal_state(current_green, red=False, yellow=True, green=False)
                current_phase = "yellow_stop"
                last_switch_time = current_time

        elif current_phase == "yellow_stop":
            if elapsed_time >= duration_yellow_stop:
                log_signal_state(current_green, red=True, yellow=False, green=False)
                log_signal_state(next_green, red=False, yellow=True, green=False)
                current_phase = "yellow_start"
                last_switch_time = current_time

        elif current_phase == "yellow_start":
            if elapsed_time >= duration_yellow_start:
                log_signal_state(next_green, red=False, yellow=False, green=True)
                current_green = next_green
                next_green = signal_order[current_green]
                current_phase = "green"
                last_switch_time = current_time

def accident_process():
    while True:
        time.sleep(3)
        with lock:
            data = shared_data.copy()
        
        accident_count = data.get("accidents", 0)

        if accident_count > 0:
            # Example rule: >1 accident = major, else minor
            severity = "major" if accident_count > 1 else "minor"

            accident_data = {
                "location": "Hyderabad, India",   # replace with GPS/metadata later
                "time": datetime.datetime.now(),
                "severity": severity,
                "nearest_hospital": "Apollo Hospital, Jubilee Hills"  # placeholder
            }

            try:
                db.collection("accidents").add(accident_data)
                log.info(f"Accident uploaded: {accident_data}")
            except Exception as e:
                log.error(f"Failed to upload accident: {e}")
