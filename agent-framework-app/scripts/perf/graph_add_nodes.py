#!/usr/bin/env python3
"""Baseline performance script: simulate adding N nodes to an in‑memory graph.
Outputs JSON with latency distribution (p50, p95, p99, mean, stddev).
Deterministic via fixed RNG seed for reproducibility.
"""
from __future__ import annotations
import argparse, json, statistics, time, random, datetime


def simulate_add_nodes(iterations: int):
    random.seed(42)
    latencies = []
    graph = {}
    for i in range(iterations):
        start = time.perf_counter()
        # Simulate variable work: create 10 nodes and link them linearly
        for j in range(10):
            node_id = f"n_{i}_{j}"
            graph[node_id] = {"edges": []}
            if j > 0:
                prev_id = f"n_{i}_{j-1}"
                graph[prev_id]["edges"].append(node_id)
        # Deterministic sleep jitter scaled small
        random.random()  # consume rng
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

    # Warmup
    simulate_add_nodes(args.warmup)
    latencies = simulate_add_nodes(args.iterations)
    metrics = dist(latencies)
    payload = {
        "metric": "graph_add_nodes",
        "iterations": args.iterations,
        **metrics,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
    }
    print(json.dumps(payload))

if __name__ == "__main__":
    main()
