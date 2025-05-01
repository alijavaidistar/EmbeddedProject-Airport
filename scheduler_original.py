import json
import time
from utils import read_planes_data, log_execution_time

def inefficient_scheduler(plane_list, num_runways=1):
    runway_schedule = []
    current_time = [0] * num_runways  # One clock per runway

    for plane in sorted(plane_list, key=lambda x: x["arrival_time"]):
        # Choose the earliest available runway
        selected_runway = current_time.index(min(current_time))

        # Simulated delay (inefficient logic)
        for _ in range(current_time[selected_runway], current_time[selected_runway] + 5):
            pass

        time.sleep(0.01)  # Simulate scheduling time

        scheduled_time = max(current_time[selected_runway], plane["arrival_time"])

        runway_schedule.append({
            "plane_id": plane["id"],
            "scheduled_at": scheduled_time,
            "type": plane["type"],
            "priority": plane["priority"],
            "runway": f"R{selected_runway + 1}"
        })

        current_time[selected_runway] = scheduled_time + 1

    return runway_schedule

def run_and_time_scheduler(num_runways=1):
    planes = read_planes_data("assets/planes.json")

    start = time.time()
    schedule = inefficient_scheduler(planes, num_runways)
    end = time.time()

    elapsed = round((end - start) * 1000, 2)  # in ms
    print(f"Inefficient scheduler took: {elapsed} ms")

    log_execution_time("Original", elapsed)
    return schedule, elapsed

if __name__ == "__main__":
    run_and_time_scheduler()