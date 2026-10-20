"""Paired microbenchmark, alternating order; stdout is JSON, never a production quality score."""
import json
import statistics
import time

import numpy as np
from test_stage_gap import reference_gap, sk


def main():
    rng = np.random.default_rng(20261020)
    pairs = []
    for _ in range(1000):
        a0 = rng.uniform(0, 20, 300)
        a1 = a0 + rng.uniform(2, 20, 300)
        b0 = rng.uniform(20, 80, 300)
        b1 = b0 + rng.uniform(2, 20, 300)
        for lo, hi in ((a0, a1), (b0, b1)):
            holes = rng.random(300) < .6
            lo[holes] = hi[holes] = np.nan
        pairs.append(((a0, a1), (b0, b1)))
    times, checks = {"original": [], "sliced": []}, {}
    for repeat in range(6):
        order = [("original", reference_gap), ("sliced", sk.gap)]
        if repeat % 2:
            order.reverse()
        for label, function in order:
            started = time.perf_counter()
            checks[label] = [function(a, b, 10) for a, b in pairs]
            times[label].append(time.perf_counter() - started)
    assert checks["original"] == checks["sliced"]
    print(json.dumps({"times": times, "median_seconds": {k: statistics.median(v) for k, v in times.items()},
                      "pairs": 1000, "repeats": 6, "identical_results": True}, indent=2))


if __name__ == "__main__":
    main()
