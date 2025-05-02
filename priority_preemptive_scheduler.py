import time
import json
from utils import read_planes_data, log_execution_time

def priority_preemptive_scheduler(plane_list, progress_callback=None):
    # Sort initially by arrival time
    plane_list.sort(key=lambda x: x['arrival_time'])
    n = len(plane_list)
    completed = 0
    current_time = 0
    schedule = []
    start = time.time()

    # Set remaining times
    for plane in plane_list:
        plane['remaining_time'] = 1  # all tasks take 1 unit to complete for simplicity
        plane['scheduled'] = False

    while completed < n:
        # Get all arrived and not completed planes
        available = [p for p in plane_list if p['arrival_time'] <= current_time and not p['scheduled']]
        if not available:
            current_time += 1
            continue

        # Pick highest priority (lowest number = highest priority)
        current_plane = sorted(available, key=lambda x: x['priority'])[0]

        scheduled_at = current_time
        current_time += current_plane['remaining_time']
        current_plane['scheduled'] = True
        completed += 1

        schedule.append({
            "plane_id": current_plane["id"],
            "scheduled_at": scheduled_at,
            "type": current_plane["type"],
            "priority": current_plane["priority"]
        })

        time.sleep(0.001)
        if progress_callback:
            elapsed = round((time.time() - start) * 1000, 2)
            progress_callback(completed, elapsed)

    end = time.time()
    elapsed_total = round((end - start) * 1000, 2)
    log_execution_time("PriorityPreemptive", elapsed_total)
    return schedule, elapsed_total

def run_pp_scheduler(progress_callback=None):
    planes = read_planes_data("assets/planes.json")
    return priority_preemptive_scheduler(planes, progress_callback)
