#!/bin/bash
set -euo pipefail
# Run from an extracted release on the Linux host, before production migration.
# Required argument: directory containing the real compressed snapshots/manifests.
test "$#" -eq 1
fixtures=$(realpath -- "$1")
cd -- "$(dirname -- "$0")"
test -d "$fixtures"
tag="duckmoo-verify-$(date +%s)-$$"
cleanup() { docker rm -f "$tag" >/dev/null 2>&1 || true; docker network rm "$tag" >/dev/null 2>&1 || true; }
trap cleanup EXIT
docker build -t duckmoo-nexus:0.3.0 ./duckmoo-nexus
docker network create --internal "$tag" >/dev/null
docker run -d --rm --name "$tag" --network "$tag" -e POSTGRES_HOST_AUTH_METHOD=trust -e POSTGRES_DB=nexus postgres:17 >/dev/null
ready=0
for ((i=0;i<30;i++)); do
 if docker exec "$tag" pg_isready -U postgres -d nexus >/dev/null 2>&1;then ready=1;break;fi
 sleep 1
done
test "$ready" -eq 1
docker run --rm --network "$tag" --entrypoint python --user "$(id -u):$(id -g)" \
 -e "DATABASE_URL=postgresql://postgres@$tag/nexus" -e NEXUS_DISPOSABLE_TEST=yes \
 --mount "type=bind,src=$fixtures,dst=/fixtures,readonly" \
 duckmoo-nexus:0.3.0 tests/verify_postgres.py
python3 release_gate.py record "$(docker image inspect --format '{{.Id}}' duckmoo-nexus:0.3.0)"
# Production containers, ports, credentials and volumes are never touched.
