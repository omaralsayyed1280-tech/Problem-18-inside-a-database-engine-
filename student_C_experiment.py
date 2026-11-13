"""Experiment 2: compare BST, B-Tree degrees, and LSM index performance.

The BST implementation and the combined index benchmark.
The official group project supplies the shared B-Tree and LSM implementations.
All timings are in-memory Python timings, not physical SSD measurements.
"""
import csv
import random
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from student_B_btree import BTreeIndex
from student_C_bst import BSTIndex
from student_D_lsm import LSMEngine

OUT = Path(__file__).resolve().parent


def time_microseconds(action, repetitions):
    """Run action once and return average elapsed microseconds per query."""
    start = time.perf_counter()
    action()
    elapsed = time.perf_counter() - start
    return elapsed * 1_000_000 / repetitions


def build_indexes(number_of_keys=100_000):
    """Build all indexes from the same shuffled 0..N-1 key set."""
    keys = list(range(number_of_keys))
    random.Random(19).shuffle(keys)  # Fixed seed makes runs repeatable.

    bst = BSTIndex()
    btrees = {degree: BTreeIndex(degree) for degree in (2, 8, 32, 128)}
    lsm = LSMEngine(memtable_limit=1024, bloom_bits=10)

    for key in keys:
        bst.insert(key)
        for tree in btrees.values():
            tree.insert(key)
        lsm.put(key, key)
    lsm.flush()

    return bst, btrees, lsm


def run_benchmarks(number_of_keys=100_000, query_count=500):
    """Measure point lookup, range query, height, and LSM Bloom-filter probes."""
    bst, btrees, lsm = build_indexes(number_of_keys)
    for tree in btrees.values():
        assert tree.validate()

    queries = random.Random(21).sample(range(number_of_keys), query_count)
    series = [("BST", bst)] + [(f"B-Tree t={t}", tree) for t, tree in btrees.items()] + [("LSM", lsm)]
    rows = []

    for name, index in series:
        if name == "LSM":
            lookup = time_microseconds(lambda: [index.get(q) for q in queries], query_count)
        else:
            lookup = time_microseconds(lambda: [index.search(q) for q in queries], query_count)
        range_time = time_microseconds(lambda: [index.range_query(q, q + 100) for q in queries], query_count)
        height = index.height() if name != "LSM" else "N/A"
        rows.append({"structure": name, "point_lookup_us": lookup, "range_query_us": range_time, "height_edges": height})
        print(f"{name:12s} point={lookup:.2f} us  range={range_time:.2f} us  height={height}")

    # Plot 2a: point lookup and range query in separate panels; BST/B-Tree/LSM all included.
    names = [row["structure"] for row in rows]
    point = [row["point_lookup_us"] for row in rows]
    ranges = [row["range_query_us"] for row in rows]
    heights = [row["height_edges"] for row in rows[:-1]]

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    axes[0].bar(names, point)
    axes[0].set_title("Point lookup (microseconds/query)")
    axes[1].bar(names, ranges)
    axes[1].set_title("Range query (microseconds/query)")
    axes[2].bar(names[:-1], heights)
    axes[2].set_title("Tree height (edges)")
    for ax in axes:
        ax.tick_params(axis="x", labelrotation=45)
        ax.grid(axis="y", alpha=0.2)
    fig.suptitle(f"Experiment 2: Index comparison ({number_of_keys:,} keys)")
    fig.tight_layout()
    fig.savefig(OUT / "plot2_indexes.png", dpi=160)
    plt.close(fig)

    # Required Bloom comparison: only query keys that definitely do not exist.
    missing = [number_of_keys + i for i in range(query_count)]
    probe_results = []
    for enabled in (False, True):
        lsm.logical_run_probes = 0
        elapsed = time_microseconds(
            lambda: [lsm.get(key, use_bloom=enabled) for key in missing], query_count
        )
        avg_probes = lsm.logical_run_probes / query_count
        probe_results.append(("With Bloom" if enabled else "Without Bloom", avg_probes, elapsed))
        print(f"{probe_results[-1][0]:14s} logical run probes/query={avg_probes:.3f}; {elapsed:.2f} us/query")

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar([x[0] for x in probe_results], [x[1] for x in probe_results])
    ax.set_ylabel("Logical SSTable run probes / missing lookup")
    ax.set_title("Bloom filter effect on missing-key queries")
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(OUT / "plot2_bloom.png", dpi=160)
    plt.close(fig)

    with (OUT / "benchmark_results.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print("Saved plot2_indexes.png, plot2_bloom.png, and benchmark_results.csv")
    return rows, probe_results


if __name__ == "__main__":
    run_benchmarks()
