#!/bin/bash
set -euo pipefail
umask 077
[[ $EUID == 0 && $# == 1 ]] || { echo 'Usage: sudo bash rollback-server.sh BACKUP_DIRECTORY' >&2; exit 1; }
backup=$(realpath -- "$1")
for entry in worker receiver; do
 test -f "$backup/duckmoo-sync/$entry.py"
 python3 -m py_compile "$backup/duckmoo-sync/$entry.py"
done
exec 7>/var/lock/duckmoo-nexus-upgrade.lock
flock -n 7
if systemctl cat duckmoo-sources.timer >/dev/null 2>&1; then
 systemctl disable --now duckmoo-sources.timer
fi
# Let additional imports finish without killing their database transaction.
exec 9>/var/lib/duckmoo-sync/source-worker.lock
flock -w 3600 9
trap 'systemctl start duckmoo-sync.timer' EXIT
systemctl stop duckmoo-sync.timer
exec 8>/var/lib/duckmoo-sync/worker.lock
flock -w 3600 8
for entry in worker receiver; do
 cp -p "$backup/duckmoo-sync/$entry.py" "/opt/duckmoo-sync/$entry.py.restore"
 mv -f "/opt/duckmoo-sync/$entry.py.restore" "/opt/duckmoo-sync/$entry.py"
done
flock -u 8
echo 'Original worker and receiver restored. Database, receipts, and queued packets retained.'
echo 'Restore the Windows task backup too if additional sources were enabled.'
