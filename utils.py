 
import json
import csv

def read_planes_data(path):
    with open(path, "r") as f:
        return json.load(f)

def log_execution_time(label, ms):
    with open("results/execution_times.csv", "a", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Test", label, ms])
