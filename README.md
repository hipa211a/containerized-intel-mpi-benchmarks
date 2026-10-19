# Containerized Intel MPI Benchmarks

IMB-MPI1 **PingPong** results comparing three ways of running MPI on AWS [**hpc7a**](https://aws.amazon.com/ec2/instance-types/hpc7a/) instances (AMD Zen 4):

| Run | Description |
|---|---|
| **Native** | Host MPI, no container (baseline) |
| **Container + bind-mounted host MPI** | Host MPI bind-mounted into the container, replacing the container's MPI. Requires ABI compatibility between the host MPI and the MPI the benchmark was built against. |
| **Container + bundled MPI** | Spack-built Open MPI 5 inside the container image, run without EFA |

Setup: Open MPI 5, 2 nodes (instances), 1 rank per node, each rank bound to 1 core. Tests run April–May 2024. Native and bind-mounted runs use Amazon's Open MPI 5 (`/opt/amazon/openmpi5`) over [EFA](https://aws.amazon.com/hpc/efa/) (Elastic Fabric Adapter, the AWS HPC interconnect).

## How it was built

All benchmarks were installed with [Spack](https://spack.io/): `spack install intel-mpi-benchmarks`.

- **Native:** installed with Spack directly on the cluster.
- **Container:** the [`Dockerfile`](Dockerfile) runs `spack install openmpi@5` and then the same benchmark install. The Spack-built Open MPI 5 exists only so the benchmark can be built; at run time it is replaced by the host MPI. The image is then converted to an Apptainer `.sif` image.

### Build the container with Podman and convert to SIF

On the cluster (e.g. the head node):

```sh
podman build -t imb:latest .
podman save --format docker-archive -o imb.tar imb:latest
apptainer build imb.sif docker-archive://imb.tar
```

To build against the host MPI instead of a Spack-built one, register `/opt/amazon/openmpi5` as an external package in the Spack config under `~/.spack` on the cluster. That stops Spack from building a new MPI. Example `~/.spack/packages.yaml`:

```yaml
packages:
  openmpi:
    externals:
    - spec: openmpi@5.0.3   # match: /opt/amazon/openmpi5/bin/mpirun --version
      prefix: /opt/amazon/openmpi5
    buildable: false
```

### Bind-mount host MPI into the container

In the Slurm run script, bind the host's Amazon Open MPI, EFA, PMIx and PRRTE directories into the container at the same paths:

```sh
# Bind directories from host into the container
export APPTAINER_BIND=/opt/amazon/openmpi5/:/opt/amazon/openmpi5/,/opt/amazon/efa/:/opt/amazon/efa/,/opt/amazon/pmix:/opt/amazon/pmix,/opt/amazon/prrte:/opt/amazon/prrte,/ebs/,/usr/lib/x86_64-linux-gnu/:/mnt/lib
```

## Results

![Latency](latency.png)

![Bandwidth](bandwidth.png)

| Metric | Native | Bind-mounted host MPI | Bundled MPI |
|---|---|---|---|
| 0-byte latency (µs) | 16.58 | 16.60 | 28.02 (+69%) |
| 64 KB latency (µs) | 26.54 | 26.66 | 121.58 (4.6x) |
| 4 MB bandwidth (MB/s) | 4436.72 | 4443.26 | 3067.87 (−31%) |

## Takeaways

- **Bind-mounting host MPI matches native performance.** Latency and bandwidth are within run-to-run noise at every message size, so the container itself adds no measurable overhead.
- **The container's bundled MPI is much slower.** It adds about 11 µs to small-message latency and peaks around 3.1 GB/s instead of 4.4 GB/s. It ran without EFA, so this is not a like-for-like comparison of the MPI itself.
- All three runs show a bandwidth dip at 128 KB. Because it appears in the native run too, it is MPI/fabric protocol behavior, not a container effect.

## Reproduce plots

Raw data lives in `data/*.csv`.

```sh
uv run --with matplotlib plot.py   # or: pip install matplotlib && python plot.py
```
