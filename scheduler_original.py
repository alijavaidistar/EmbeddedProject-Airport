 
import json
import time
from utils import read_planes_data, log_execution_time

# Simulate 1 runway only for now
def inefficient_scheduler(plane_list):
    runway_schedule = []
    current_time = 0

    for plane in sorted(plane_list, key=lambda x: x["arrival_time"]):
        # Nested loop simulating time scanning (inefficient on purpose)
        for t in range(current_time, current_time + 5):  # Useless scan
            pass

        # Simulate that it takes 1 sec to schedule each plane
        time.sleep(0.01)  # Simulated delay

        # "Schedule" plane
        runway_schedule.append({
            "plane_id": plane["id"],
            "scheduled_at": max(current_time, plane["arrival_time"]),
            "type": plane["type"],
            "priority": plane["priority"]
        })

        current_time = runway_schedule[-1]["scheduled_at"] + 1

    return runway_schedule


def run_and_time_scheduler():
    planes = read_planes_data("assets/planes.json")

    start = time.time()
    schedule = inefficient_scheduler(planes)
    end = time.time()

    elapsed = round((end - start) * 1000, 2)  # in ms
    print(f"Inefficient scheduler took: {elapsed} ms")

    log_execution_time("Original", elapsed)
    return schedule, elapsed


if __name__ == "__main__":
    run_and_time_scheduler()
