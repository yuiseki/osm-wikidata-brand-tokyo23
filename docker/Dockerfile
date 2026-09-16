# The environment this dataset is built in, pinned so that a rebuild is a
# rebuild and not a different run that happens to produce a similar file.
#
# Three things decide the output and all three are here. Python, because the
# scripts are Python. psycopg, because it reads PostGIS. lbzip2, because the
# 96 GiB dump is read through it and bzip2 alone would take hours on one core.
#
# PostGIS itself is not here: it belongs to osm-tokyo23-src-2026-08, which
# pins postgis/postgis:16-3.4 and osm2pgsql 1.11.0 and is where the frozen
# extract is built. This container connects to it.
# Pinned by digest, not by tag. `bookworm-slim` moves; this does not.
FROM debian:bookworm-slim@sha256:88200866dfff7ea7f5cbcb6ec7c8a701889efe6fe859fe64d6990e4b07ea4171

# The versions bookworm carries today, written down rather than taken as
# whatever the base happens to have, so that a base moving under us is a build
# failure and not a different dataset. Debian removes old versions from the
# archive, so these will stop resolving eventually; when they do, the failure
# is the point.
ARG PYTHON_VERSION=3.11.2-1+b1
ARG LBZIP2_VERSION=2.5-2.3
ARG PIP_VERSION=23.0.1+dfsg-1
ARG PSYCOPG_VERSION=3.3.2

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      python3=${PYTHON_VERSION} \
      python3-pip=${PIP_VERSION} \
      lbzip2=${LBZIP2_VERSION} \
      ca-certificates \
 && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --break-system-packages \
      "psycopg[binary]==${PSYCOPG_VERSION}" \
 && python3 -c "import psycopg; assert psycopg.__version__ == '${PSYCOPG_VERSION}'"

WORKDIR /work
