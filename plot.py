"""Plot IMB PingPong latency and bandwidth for native vs containerized runs.

Usage: uv run --with matplotlib plot.py
"""
import csv
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).parent
RUNS = [  # (csv, label, color, marker)
    ("native.csv", "Native (host MPI, no container)", "#2a78d6", "o"),
    ("container_host_mpi.csv", "Container + bind-mounted host MPI", "#eb6834", "s"),
    ("container_bundled_mpi.csv", "Container + bundled MPI", "#1baf7a", "^"),
]


def load(name):
    with open(ROOT / "data" / name) as f:
        rows = list(csv.DictReader(f))
    # 0-byte row dropped: can't sit on a log axis (its latency is in README)
    rows = [r for r in rows if int(r["bytes"]) > 0]
    return ([int(r["bytes"]) for r in rows],
            [float(r["t_usec"]) for r in rows],
            [float(r["mbytes_per_sec"]) for r in rows])


def plot(col, ylabel, title, out, logy):
    fig, ax = plt.subplots(figsize=(8, 5))
    for i, (name, label, color, marker) in enumerate(RUNS):
        x, lat, bw = load(name)
        # bind-mount (i == 1) as points only, on top of the native line it overlaps
        ax.plot(x, (lat, bw)[col], label=label, color=color, marker=marker,
                markersize=(9, 5, 7)[i], linewidth=2, zorder=(2, 3, 1)[i],
                linestyle="none" if i == 1 else "-",
                markerfacecolor="white" if i == 0 else color)
    ax.set_xscale("log", base=2)
    ticks = [4 ** k for k in range(12)]
    ax.set_xticks(ticks, [f"{t >> 20}M" if t >= 2**20 else f"{t >> 10}K" if t >= 1024
                          else str(t) for t in ticks])
    if logy:
        ax.set_yscale("log")
    ax.set_xlabel("Message size (bytes)")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, which="major", color="#e4e3df", linewidth=0.8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(ROOT / out, dpi=150)


plot(0, "Latency t (µs, log)", "IMB PingPong latency — hpc7a, 2 nodes, 1 rank/node",
     "latency.png", logy=True)
plot(1, "Bandwidth (MB/s)", "IMB PingPong bandwidth — hpc7a, 2 nodes, 1 rank/node",
     "bandwidth.png", logy=False)
