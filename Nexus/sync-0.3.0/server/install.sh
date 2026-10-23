#!/bin/bash
set -euo pipefail
umask 077
if [[ $EUID != 0 || $# -lt 1 || $# -gt 2 ]]; then
  echo 'Usage: sudo bash server/install.sh POSTGRES_CONTAINER [DOCKER_NETWORK]' >&2; exit 1
fi
cd -- "$(dirname -- "$0")"
id kenzieduckmoo >/dev/null
/usr/bin/docker image inspect duckmoo-nexus:0.1.0 >/dev/null
/usr/bin/docker inspect "$1" >/dev/null
test -f /home/kenzieduckmoo/nexus/releases/v0.1.0/duckmoo-nexus/.env
install -d -m 755 /opt/duckmoo-sync /etc/duckmoo-sync /var/lib/duckmoo-sync
install -d -m 700 -o kenzieduckmoo -g "$(id -gn kenzieduckmoo)" /var/lib/duckmoo-sync/inbox
install -d -m 755 /var/lib/duckmoo-sync/receipts
install -d -m 700 /var/lib/duckmoo-sync/staging
install -m 644 sync_core.py receiver.py worker.py /opt/duckmoo-sync/
# Existing configuration is preserved on reinstallation.
if [[ ! -e /etc/duckmoo-sync/config.json ]]; then
python3 - "$1" "${2:-}" <<'PY'
import json, pwd, sys
p = pwd.getpwnam('kenzieduckmoo')
with open('/etc/duckmoo-sync/config.json', 'x') as f:
    json.dump(dict(postgres_container=sys.argv[1], network=sys.argv[2], uid=p.pw_uid, gid=p.pw_gid,
        env_file='/home/kenzieduckmoo/nexus/releases/v0.1.0/duckmoo-nexus/.env'), f, indent=2)
PY
fi
install -m 644 duckmoo-sync.service duckmoo-sync.timer /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now duckmoo-sync.timer
echo 'Installed. Add the restricted Windows public key using README.md, then test.'
