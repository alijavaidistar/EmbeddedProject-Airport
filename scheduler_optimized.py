import time
import heapq
from utils import read_planes_data, log_execution_time

def optimized_scheduler(plane_list, num_runways=1, progress_callback=None):
    plane_list.sort(key=lambda x: (x["arrival_time"], x["priority"]))
    heap = [(p["arrival_time"], p["priority"], p["id"], p) for p in plane_list]
    heapq.heapify(heap)

    runways = [0] * num_runways  # Availability time for each runway
    schedule = []
    current_time = 0
    start = time.time()

    count = 0
    while heap:
        _, priority, plane_id, plane = heapq.heappop(heap)

        # Find the earliest available runway
        runway_id = min(range(num_runways), key=lambda r: runways[r])
        scheduled_at = max(runways[runway_id], plane["arrival_time"])
        runways[runway_id] = scheduled_at + 1

        schedule.append({
            "plane_id": plane["id"],
            "scheduled_at": scheduled_at,
            "type": plane["type"],
            "priority": priority,
            "arrival_time": plane["arrival_time"],
            "runway_id": runway_id + 1  # 1-based for readability
        })

        count += 1
        if progress_callback:
            elapsed = round((time.time() - start) * 1000, 2)
            progress_callback(count, elapsed)

    end = time.time()
    elapsed_total = round((end - start) * 1000, 2)
    log_execution_time("Optimized", elapsed_total)

    return schedule, elapsed_total

def run_and_time_scheduler(num_runways=1, progress_callback=None):
    planes = read_planes_data("assets/planes.json")
    
    start_time = time.time()
    schedule = optimized_scheduler(planes, num_runways, progress_callback)
    end_time = time.time()

    elapsed_ms = round((end_time - start_time) * 1000, 2)
    log_execution_time("Optimized", elapsed_ms)
    
    return schedule, elapsed_ms