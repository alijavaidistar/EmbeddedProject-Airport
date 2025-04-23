 
import time
import heapq
from utils import read_planes_data, log_execution_time

def optimized_scheduler(plane_list):
    # Sort once by arrival_time (then by priority)
    plane_list.sort(key=lambda x: (x["arrival_time"], x["priority"]))

    # Use a min-heap with a tie-breaker on plane id
    heap = [(p["arrival_time"], p["priority"], p["id"], p) for p in plane_list]
    heapq.heapify(heap)

    runway_schedule = []
    current_time = 0

    while heap:
        arrival_time, priority, plane_id, plane = heapq.heappop(heap)

        # Schedule plane
        scheduled_at = max(current_time, arrival_time)
        runway_schedule.append({
            "plane_id": plane["id"],
            "scheduled_at": scheduled_at,
            "type": plane["type"],
            "priority": priority
        })

        current_time = scheduled_at + 1

    return runway_schedule



def run_and_time_scheduler():
    planes = read_planes_data("assets/planes.json")

    start = time.time()
    schedule = optimized_scheduler(planes)
    end = time.time()

    elapsed = round((end - start) * 1000, 2)  # in ms
    print(f"Optimized scheduler took: {elapsed} ms")

    log_execution_time("Optimized", elapsed)
    return schedule, elapsed


if __name__ == "__main__":
    run_and_time_scheduler()
