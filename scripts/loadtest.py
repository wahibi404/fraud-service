"""Tiny load generator (no extra tools needed):

    python scripts/loadtest.py                     # 2000 requests, 25 at a time
    python scripts/loadtest.py -n 500 -c 50 --url http://localhost:8000/v1/predict
"""
import argparse
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx

parser = argparse.ArgumentParser()
parser.add_argument("--url", default="http://localhost:8000/v1/predict")
parser.add_argument("-n", type=int, default=2000, help="total requests")
parser.add_argument("-c", type=int, default=25, help="concurrent clients")
parser.add_argument("--body", type=Path, default=Path("payloads/sample.json"))
args = parser.parse_args()

body = args.body.read_bytes()
client = httpx.Client(limits=httpx.Limits(max_connections=args.c), timeout=30)


def one(_: int) -> tuple[float, int]:
    t0 = time.perf_counter()
    r = client.post(args.url, content=body, headers={"content-type": "application/json"})
    return (time.perf_counter() - t0) * 1000, r.status_code


t0 = time.perf_counter()
with ThreadPoolExecutor(args.c) as pool:
    results = list(pool.map(one, range(args.n)))
wall = time.perf_counter() - t0

ms = sorted(r[0] for r in results)
bad = sum(1 for r in results if r[1] >= 400)
print(f"requests: {args.n}  concurrency: {args.c}  wall: {wall:.1f}s")
print(f"p50: {statistics.median(ms):.1f} ms   p99: {ms[int(len(ms) * 0.99) - 1]:.1f} ms   "
      f"max: {ms[-1]:.1f} ms")
print(f"throughput: {args.n / wall:.0f} req/s   non-2xx: {bad}")
