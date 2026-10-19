#!/bin/bash
# Example: IMB PingPong, 2 nodes x 1 rank, using the container with host MPI
# bind-mounted over it. Adjust partition and paths for your cluster.
#SBATCH --job-name=imb-pingpong
#SBATCH --partition=hpc7a
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=1
#SBATCH --exclusive
#SBATCH --output=imb-pingpong-%j.out

SIF=/ebs/imb.sif

# Bind directories from host into the container
export APPTAINER_BIND=/opt/amazon/openmpi5/:/opt/amazon/openmpi5/,/opt/amazon/efa/:/opt/amazon/efa/,/opt/amazon/pmix:/opt/amazon/pmix,/opt/amazon/prrte:/opt/amazon/prrte,/ebs/,/usr/lib/x86_64-linux-gnu/:/mnt/lib

# Make the benchmark load the bound host MPI and libfabric instead of the
# Spack-built placeholder. /mnt/lib (host system libs) supplies EFA's
# rdma-core dependencies; keep it last. Use lib64 if your host has that layout.
export APPTAINERENV_LD_LIBRARY_PATH=/opt/amazon/openmpi5/lib:/opt/amazon/efa/lib:/mnt/lib

# Host mpirun launches one container per rank, each bound to 1 core.
/opt/amazon/openmpi5/bin/mpirun -np 2 --map-by ppr:1:node --bind-to core \
  apptainer exec "$SIF" IMB-MPI1 PingPong
