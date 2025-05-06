import json
import time
from utils import read_planes_data, log_execution_time

def round_robin_scheduler(plane_list, time_quantum=2, progress_callback=None):
    """Round Robin scheduler with accurate progress plotting for completed planes."""

    for plane in plane_list:
        if plane['type'].lower() == 'emergency':
            plane['remaining_time'] = time_quantum * 1
        elif plane['type'].lower() == 'cargo':
            plane['remaining_time'] = time_quantum * 3
        else:
            plane['remaining_time'] = time_quantum * 2

    queue = sorted(plane_list, key=lambda x: x['arrival_time'])
    current_time = 0
    runway_schedule = []
    total_planes = len(queue)
    completed_planes = 0

    start_time = time.time()

    while queue:
        plane = queue.pop(0)
        execute_time = min(plane['remaining_time'], time_quantum)
        current_time += execute_time
        plane['remaining_time'] -= execute_time

        runway_schedule.append({
            "plane_id": plane["id"],
            "scheduled_at": current_time - execute_time,
            "completed_at": current_time,
            "type": plane["type"],
            "priority": plane["priority"],
            "runway_used": execute_time
        })

        if plane['remaining_time'] <= 0:
            completed_planes += 1
            if progress_callback:
                elapsed = round((time.time() - start_time) * 1000, 2)
                progress_callback(completed_planes, elapsed)
        else:
            queue.append(plane)

    total_elapsed = round((time.time() - start_time) * 1000, 2)
    log_execution_time("Round Robin", total_elapsed)

    return runway_schedule, total_elapsed

def run_rr_scheduler(progress_callback=None):
    try:
        planes = read_planes_data("assets/planes.json")
        if not planes:
            raise ValueError("No plane data found.")
        return round_robin_scheduler(planes, time_quantum=2, progress_callback=progress_callback)
    except Exception as e:
        print(f"[Round Robin Error] {str(e)}")
        return [], 0