#!/bin/env pyhton
import os

path = "dataset_1_1_500_v2/experiment_results"
filtered_path = "dataset_1_1_500_filtered/experiment_results"
filter_str = "not (src 127.0.0.1 and dst 127.0.0.1)"

os.makedirs(filtered_path, exist_ok=True)
for root, dirs, files in os.walk(path):
    for f in files:
        if f.endswith(".pcap"):
            p = f"{root}/{f}"
            new_p = p.replace(path, filtered_path)
            os.makedirs(root.replace(path, filtered_path), exist_ok=True)

            try:
                if os.path.getsize(new_p) == 0:
                    raise Exception("File is empty")
            except Exception: # also if FileNotFoundError
                os.popen(f"tcpdump -ns 0  -r {p} '{filter_str}' -w {new_p}")
            

