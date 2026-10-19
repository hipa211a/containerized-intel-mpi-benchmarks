# Intel MPI Benchmarks built with Spack. Spack also builds Open MPI 5 inside the
# image; it is only a placeholder that gets replaced by the host's ABI-compatible
# /opt/amazon/openmpi5 (bind-mounted) at run time.
FROM ubuntu:22.04

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      build-essential gfortran git python3 curl ca-certificates file \
      patch tar gzip unzip bzip2 xz-utils gnupg2 \
 && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 --branch v0.21.2 https://github.com/spack/spack.git /opt/spack
ENV PATH=/opt/spack/bin:$PATH

RUN spack compiler find \
 && spack install openmpi@5 \
 && spack install intel-mpi-benchmarks ^openmpi@5 \
 && ln -s $(spack location -i intel-mpi-benchmarks)/bin/IMB-* /usr/local/bin/ \
 && spack clean -a
