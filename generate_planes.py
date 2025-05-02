import json
import random
import os

def generate_planes(num_planes=100):
    planes = []
    for i in range(1, num_planes + 1):
        arrival = random.randint(1, 300)
        plane = {
            "id": f"PL{1000 + i}",
            "type": random.choice(["landing", "takeoff"]),
            "priority": random.randint(1, 3),
            "arrival_time": arrival,
            "deadline": random.randint(arrival + 10, arrival + 300)
        }
        planes.append(plane)

    os.makedirs("assets", exist_ok=True)
    with open("assets/planes.json", "w") as f:
        json.dump(planes, f, indent=4)


if __name__ == "__main__":
    generate_planes(100)  # You can change this to 500 or 1000
