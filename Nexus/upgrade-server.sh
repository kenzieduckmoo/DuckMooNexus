#!/bin/bash
set -euo pipefail
umask 077
if [[ $EUID != 0 || $# != 3 ]]; then
 echo 'Usage: sudo bash upgrade-server.sh POSTGRES_CONTAINER IMPORTER_ROLE GRAFANA_ROLE' >&2; exit 1
fi
cd -- "$(dirname -- "$0")"
pg=$1; importer=$2; grafana=$3
exec 7>/var/lock/duckmoo-nexus-upgrade.lock
flock -n 7
bash ./preflight.sh "$pg"
for source in sync_core.py receiver.py worker.py; do
 cmp "/opt/duckmoo-sync/$source" "sync-reference/duckmoo-nexus-sync-0.2.0/server/$source" || {
  echo 'Deployed sync differs from v0.2.0. Reconcile before upgrading.' >&2; exit 1;
 }
done
image=$(docker image inspect --format '{{.Id}}' duckmoo-nexus:0.3.0)
python3 release_gate.py check "$image"
for unit in duckmoo-sources.service duckmoo-sources.timer; do
 if [[ -e /etc/systemd/system/$unit ]]; then
  cmp "/etc/systemd/system/$unit" "sync-0.3.0/server/$unit"
 fi
done
if systemctl is-active --quiet duckmoo-sources.timer; then
 echo 'Additional-source timer is already active; inspect before upgrading.' >&2; exit 1
fi
systemd-analyze verify sync-0.3.0/server/duckmoo-sources.{service,timer}
backup="/home/kenzieduckmoo/nexus/backups/pre-0.3.0-$(date +%Y%m%dT%H%M%S)-$$"
mkdir -p "$backup"
cp -a /opt/duckmoo-sync "$backup/"
cp -a /etc/duckmoo-sync "$backup/config"
docker exec "$pg" sh -c 'exec pg_dump -Fc -U "$POSTGRES_USER" -d nexus' > "$backup/nexus.dump"
test -s "$backup/nexus.dump"
docker exec -i "$pg" pg_restore --list < "$backup/nexus.dump" > "$backup/dump-contents.txt"
test -s "$backup/dump-contents.txt"
# Stage immutable imports; old receivers keep the untouched v0.2.0 modules.
stage="/opt/duckmoo-sync/release-$(date +%Y%m%dT%H%M%S)-$$"
install -d -m 755 "$stage"
install -m 644 sync-0.3.0/server/{worker,receiver,sync_core}.py "$stage/"
install -m 644 duckmoo-nexus/{bundle,snapshots}.py "$stage/"
python3 -m py_compile "$stage/"*.py
for entry in receiver worker; do
 cat > "$stage/$entry.launcher" <<EOF
#!/usr/bin/python3
import runpy
import sys
sys.path.insert(0, "$stage")
runpy.run_path("$stage/$entry.py", run_name="__main__")
EOF
done
# Apply all additive migrations and grants in one transaction, with bounded locks.
{
 echo "SET lock_timeout = '10s';"
 cat duckmoo-nexus/sql/00{2,3,4}_*.sql duckmoo-nexus/sql/grant_roles.psql
} | docker exec -i "$pg" sh -c 'exec psql -X -v ON_ERROR_STOP=1 -1 -U "$POSTGRES_USER" -d nexus -v "importer_role=$1" -v "grafana_role=$2"' sh "$importer" "$grafana"
changed=0
recover() {
 rc=$?
 trap - EXIT
 set +e
 if (( rc != 0 && changed )); then
  for entry in receiver worker; do
   cp -p "$backup/duckmoo-sync/$entry.py" "/opt/duckmoo-sync/$entry.py.restore"
   mv -f "/opt/duckmoo-sync/$entry.py.restore" "/opt/duckmoo-sync/$entry.py"
  done
  echo "Activation failed; original launchers restored. Backup: $backup" >&2
 fi
 systemctl start duckmoo-sync.timer || rc=1
 exit "$rc"
}
trap recover EXIT
systemctl stop duckmoo-sync.timer
# Wait for the active worker; never kill an in-flight import.
exec 8>/var/lib/duckmoo-sync/worker.lock
flock -w 3600 8
changed=1
for entry in worker receiver; do
 install -m 644 "$stage/$entry.launcher" "/opt/duckmoo-sync/$entry.py.new"
 mv -f "/opt/duckmoo-sync/$entry.py.new" "/opt/duckmoo-sync/$entry.py"
done
flock -u 8
install -m 644 sync-0.3.0/server/duckmoo-sources.{service,timer} /etc/systemd/system/
systemctl daemon-reload
systemctl start duckmoo-sync.timer
systemctl is-active --quiet duckmoo-sync.timer
changed=0
printf 'Upgrade activated. Backup: %s\n' "$backup"
echo 'Check a fresh original Journalator receipt before enabling additional Windows sources.'
echo 'The new source timer is installed but disabled. After the receipt check: systemctl enable --now duckmoo-sources.timer'
