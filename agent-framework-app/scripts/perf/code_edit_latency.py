#!/usr/bin/env python3
"""Simulate code edit diff latency measurement.
Produces JSON metrics distribution similar to graph_add_nodes.
Deterministic workload using fixed seed.
"""
from __future__ import annotations
import argparse
import json
import statistics
import time
import random
import difflib
import datetime

SAMPLE_OLD = """def add(a, b):\n    return a + b\n"""
SAMPLE_NEW_VARIANTS = [
    """def add(a, b):\n    # optimized path\n    return (a + b)\n""",
    """def add(a: int, b: int) -> int:\n    return a + b\n""",
    """def add(a, b):\n    if b == 0: return a\n    return a + b\n""",
]

def simulate_code_diff(iterations: int):
    random.seed(1337)
    latencies = []
    for i in range(iterations):
        start = time.perf_counter()
        variant = SAMPLE_NEW_VARIANTS[i % len(SAMPLE_NEW_VARIANTS)]
        # Simulate diff generation
        list(difflib.unified_diff(SAMPLE_OLD.splitlines(), variant.splitlines()))
        end = time.perf_counter()
        latencies.append((end - start) * 1000)
    return latencies


def dist(latencies):
    latencies_sorted = sorted(latencies)
    def pct(p):
        if not latencies_sorted:
            return 0.0
        k = (len(latencies_sorted)-1) * p
        f = int(k)
        c = min(f+1, len(latencies_sorted)-1)
        if f == c:
            return latencies_sorted[f]
        return latencies_sorted[f] + (latencies_sorted[c]-latencies_sorted[f]) * (k-f)
    return {
        "p50_ms": pct(0.50),
        "p95_ms": pct(0.95),
        "p99_ms": pct(0.99),
        "mean_ms": statistics.fmean(latencies_sorted) if latencies_sorted else 0.0,
        "stddev_ms": statistics.pstdev(latencies_sorted) if len(latencies_sorted) > 1 else 0.0,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=10)
    parser.add_argument("--warmup", type=int, default=1)
    args = parser.parse_args()
    simulate_code_diff(args.warmup)
    latencies = simulate_code_diff(args.iterations)
    metrics = dist(latencies)
    payload = {
        "metric": "code_edit_diff",
        "iterations": args.iterations,
        **metrics,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
    }
    print(json.dumps(payload))

if __name__ == "__main__":
    main()
