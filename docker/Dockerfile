# The environment this dataset is built in, pinned so that a rebuild is a
# rebuild and not a different run that happens to produce a similar file.
#
# Three things decide the output and all three are here. Python, because the
# scripts are Python. osmium-tool, because the extract is read with it.
# lbzip2, because the 96 GiB dump is read through it and bzip2 alone would
# take hours on one core.
#
# PostGIS is gone from this image and from the code. Reading the extract
# through osm2pgsql cost this dataset its two most important keys: that tool
# promotes `name` and `brand` to columns of their own, so the hstore column
# the build read held every name key except those two.
# Pinned by digest, not by tag. `bookworm-slim` moves; this does not.
FROM debian:bookworm-slim@sha256:88200866dfff7ea7f5cbcb6ec7c8a701889efe6fe859fe64d6990e4b07ea4171

# The versions bookworm carries today, written down rather than taken as
# whatever the base happens to have, so that a base moving under us is a build
# failure and not a different dataset. Debian removes old versions from the
# archive, so these will stop resolving eventually; when they do, the failure
# is the point.
ARG PYTHON_VERSION=3.11.2-1+b1
ARG LBZIP2_VERSION=2.5-2.3
ARG OSMIUM_VERSION=1.15.0-1

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      python3=${PYTHON_VERSION} \
      lbzip2=${LBZIP2_VERSION} \
      osmium-tool=${OSMIUM_VERSION} \
      ca-certificates \
 && rm -rf /var/lib/apt/lists/* \
 && osmium --version | grep -q "osmium version 1.15.0"

WORKDIR /work
