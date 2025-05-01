import time
import heapq
from utils import read_planes_data, log_execution_time

def optimized_scheduler(plane_list, num_runways=1, progress_callback=None):
    plane_list.sort(key=lambda x: (x["arrival_time"], x["priority"]))
    heap = [(p["arrival_time"], p["priority"], p["id"], p) for p in plane_list]
    heapq.heapify(heap)

    runway_schedule = []
    current_time = [0] * num_runways  # Independent clocks for each runway
    start = time.time()

    count = 0
    while heap:
        arrival_time, priority, plane_id, plane = heapq.heappop(heap)

        selected_runway = current_time.index(min(current_time))
        scheduled_at = max(current_time[selected_runway], arrival_time)

        runway_schedule.append({
            "plane_id": plane["id"],
            "scheduled_at": scheduled_at,
            "type": plane["type"],
            "priority": priority,
            "runway": f"R{selected_runway + 1}"
        })

        current_time[selected_runway] = scheduled_at + 1
        count += 1

        time.sleep(0.001)

        if progress_callback:
            elapsed = round((time.time() - start) * 1000, 2)
            progress_callback(count, elapsed)

    end = time.time()
    elapsed_total = round((end - start) * 1000, 2)
    log_execution_time("Optimized", elapsed_total)

    return runway_schedule, elapsed_total

def run_and_time_scheduler(num_runways=1, progress_callback=None):
    planes = read_planes_data("assets/planes.json")
    return optimized_scheduler(planes, num_runways, progress_callback)