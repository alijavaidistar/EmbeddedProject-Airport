import time
import json
from utils import read_planes_data, log_execution_time


def edf_scheduler(plane_list, progress_callback=None):
    # Sort planes based on deadline
    sorted_planes = sorted(plane_list, key=lambda x: x['deadline'])

    runway_schedule = []
    current_time = 0
    start = time.time()

    for count, plane in enumerate(sorted_planes, 1):
        scheduled_at = max(current_time, plane['arrival_time'])
        runway_schedule.append({
            "plane_id": plane["id"],
            "scheduled_at": scheduled_at,
            "type": plane["type"],
            "priority": plane["priority"]
        })

        current_time = scheduled_at + 1

        # simulate small delay for UI responsiveness
        time.sleep(0.001)

        if progress_callback:
            elapsed = round((time.time() - start) * 1000, 2)
            progress_callback(count, elapsed)

    end = time.time()
    elapsed_total = round((end - start) * 1000, 2)
    log_execution_time("EDF", elapsed_total)
    return runway_schedule, elapsed_total


def run_edf_scheduler(progress_callback=None):
    planes = read_planes_data("assets/planes.json")
    return edf_scheduler(planes, progress_callback)
