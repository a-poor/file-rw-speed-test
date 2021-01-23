
import os
import time
import json
from pathlib import Path
from itertools import chain
from tqdm import tqdm

def time_write_data(fn: str, n_bytes: int) -> int:
    start = time.perf_counter_ns()
    with open(fn,"wb") as f:
        f.write(bytes(n_bytes))
    return time.perf_counter_ns() - start

def time_read_data(fn: str) -> int:
    start = time.perf_counter_ns()
    with open(fn,"rb") as f:
        _ = f.read()
    return time.perf_counter_ns() - start

def time_rw(fn: str, n_bytes: int) -> (int,int):
    w = time_write_data(fn,n_bytes)
    r = time_read_data(fn)
    return w, r

def get_mean_std(data):
    n = len(data)
    mean = sum(data) / n
    std = (sum((d-mean)**2 for d in data) / n) ** 0.5
    return mean, std

# def multi_run(fn: str, n_bytes: int = 0, n_runs: int = 1) -> dict:
#     if n_bytes < 1e3:
#         desc = f"{n_bytes:6,d} b "
#     elif n_bytes < 1e6:
#         desc = f"{int(n_bytes/1e3):6,d} KB"
#     elif n_bytes < 1e9:
#         desc = f"{int(n_bytes/1e6):6,d} MB"
#     elif n_bytes < 1e12:
#         desc = f"{int(n_bytes/1e9):6,d} GB"
#     else:
#         desc = f"{n_bytes:,d} bytes"
#     itr = tqdm(range(n_runs),total=n_runs,desc=desc,ncols=80)
#     data = (time_rw(fn,n_bytes) for _ in itr)
#     write_data, read_data = zip(*data)
#     wmean, wstd = get_mean_std(write_data)
#     rmean, rstd = get_mean_std(read_data)
#     return {
#         "write-mean-ns": wmean,
#         "write-std-ns": wstd,
#         "read-mean-ns": rmean,
#         "read-std-ns": rstd
#     }
# 
# def grid_run(fn: str, n_bytes: [int], n_repeats: int = 100) -> [dict]:
#     return [{"n-bytes":nb,**multi_run(fn,nb,n_repeats)} for nb in n_bytes]

def multi_run(fn: str, n_bytes: int = 0, n_runs: int = 1) -> dict:
    if n_bytes < 1e3:
        desc = f"{n_bytes:5,.1f} B "
    elif n_bytes < 1e6:
        desc = f"{int(n_bytes/1e3):5,.1f} KB"
    elif n_bytes < 1e9:
        desc = f"{int(n_bytes/1e6):5,.1f} MB"
    elif n_bytes < 1e12:
        desc = f"{int(n_bytes/1e9):5,.1f} GB"
    else:
        desc = f"{n_bytes:,.1f} bytes"
    itr = tqdm(range(n_runs),total=n_runs,desc=desc,ncols=80)
    data = (time_rw(fn,n_bytes) for _ in itr)
    data = [dict(zip(("write-ns","read-ns"),d)) for d in data]
    return [{"n-bytes":n_bytes,**d} for d in data]

def grid_run(fn: str, n_bytes: [int], n_repeats: int = 100) -> [dict]:
    return list(chain(*(multi_run(fn,nb,n_repeats) for nb in n_bytes)))


if __name__ == "__main__":
    # Configs
    TMP_FILE = Path("tmp.file")
    N_BYTES = [10**i for i in range(10)]
    N_REPEATS = 100
    OUTPUT = Path("rw-data.json")

    # Setup
    print("Starting...")
    TMP_FILE.touch()

    # Run Test
    print("Testing...")
    try:
        data = grid_run(
            TMP_FILE,
            N_BYTES,
            N_REPEATS
        )
        
        # Cleanup
        print("Cleaning up...")
        OUTPUT.write_text(json.dumps(data,indent=2))
    finally:
        TMP_FILE.unlink()
    print("Done.")


