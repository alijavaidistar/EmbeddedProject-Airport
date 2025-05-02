import time
import json
from utils import read_planes_data, log_execution_time

def round_robin_scheduler(plane_list, time_quantum=2, progress_callback=None):
    # Simulate each plane as a task with a required time to complete (randomized for simplicity)
    for plane in plane_list:
        plane['remaining_time'] = time_quantum * 2  # simulate short job duration

    queue = sorted(plane_list, key=lambda x: x['arrival_time'])
    current_time = 0
    runway_schedule = []
    start = time.time()
    count = 0

    while queue:
        plane = queue.pop(0)
        execute_time = min(plane['remaining_time'], time_quantum)
        scheduled_at = max(current_time, plane['arrival_time'])
        current_time = scheduled_at + execute_time
        plane['remaining_time'] -= execute_time

        runway_schedule.append({
            "plane_id": plane["id"],
            "scheduled_at": scheduled_at,
            "type": plane["type"],
            "priority": plane["priority"]
        })

        if plane['remaining_time'] > 0:
            queue.append(plane)  # re-add to queue if not finished

        count += 1
        time.sleep(0.001)
        if progress_callback:
            elapsed = round((time.time() - start) * 1000, 2)
            progress_callback(count, elapsed)

    end = time.time()
    elapsed_total = round((end - start) * 1000, 2)
    log_execution_time("RoundRobin", elapsed_total)
    return runway_schedule, elapsed_total

def run_rr_scheduler(progress_callback=None):
    planes = read_planes_data("assets/planes.json")
    return round_robin_scheduler(planes, time_quantum=2, progress_callback=progress_callback)
