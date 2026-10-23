#!/bin/bash
set -euo pipefail
test "$#" -eq 1
pg=$1
docker inspect --format '{{.Name}} {{.Config.Image}} {{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}' "$pg"
test -f /etc/duckmoo-sync/config.json
test -f /opt/duckmoo-sync/worker.py
systemctl is-active duckmoo-sync.timer
docker exec "$pg" sh -c 'exec psql -X -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d nexus -c "SELECT version FROM nexus.schema_migrations ORDER BY version; SELECT namespace,count(*) FROM nexus.transactions GROUP BY namespace;"'
sha256sum /opt/duckmoo-sync/{worker,receiver,sync_core}.py
echo 'Read-only preflight complete. Compare deployed source to bundled sync-reference before upgrading.'
