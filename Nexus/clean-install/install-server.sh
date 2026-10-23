#!/bin/bash
set -euo pipefail
[[ $EUID == 0 ]] || { echo 'Run with sudo' >&2; exit 1; }
cd -- "$(dirname -- "$0")"
exec 9>/var/lock/duckmoo-nexus-clean-install.lock
flock -n 9
command -v docker >/dev/null || {
 apt-get update
 apt-get install -y docker.io docker-compose-v2
}
docker compose version >/dev/null || { apt-get update; apt-get install -y docker-compose-v2; }
systemctl enable --now docker
# Retire the disposable Nexus runtime. Source spools and historical files stay.
for unit in duckmoo-sync.timer duckmoo-sources.timer duckmoo-sync.service duckmoo-sources.service; do
 systemctl disable --now "$unit" 2>/dev/null || true
done
systemctl disable --now grafana-server.service 2>/dev/null || true
target=/opt/duckmoo-nexus-clean
mkdir -p "$target" /var/lib/duckmoo-nexus-sources
if [[ -f "$target/compose.yaml" ]]; then
 docker compose --project-directory "$target" down -v --remove-orphans
fi
# Stop only earlier Nexus containers (never prune other applications or volumes).
while read -r id name image; do
 case "$name" in *nexus*|duckmoo-postgres*|duckmoo-grafana*) docker stop "$id"; continue ;; esac
 case "$image" in grafana/grafana*|grafana/grafana-oss*)
  if docker port "$id" | grep -q ':3000$'; then docker stop "$id"; fi ;;
 esac
done < <(docker ps --format '{{.ID}} {{.Names}} {{.Image}}')
cp -a app provisioning compose.yaml receiver.py verify-server.py "$target/"
chmod -R a+rX "$target/app" "$target/provisioning"
install -m 644 receiver.py "$target/receiver.py"
python3 - "$target" <<'PY'
import pathlib,secrets,sys
p=pathlib.Path(sys.argv[1])/'.env'
p.write_text('\n'.join(k+'='+secrets.token_hex(24) for k in
 ('POSTGRES_PASSWORD','GF_DB_PASSWORD','GRAFANA_PASSWORD'))+'\n')
p.chmod(0o600)
PY
id duckmoo-nexus-sync >/dev/null 2>&1 || useradd --create-home --shell /bin/sh duckmoo-nexus-sync
# Dedicated account permits only the receiver via a root-owned sudo rule.
install -d -m 700 -o duckmoo-nexus-sync -g duckmoo-nexus-sync /home/duckmoo-nexus-sync/.ssh
python3 - "$PWD/sync-key.pub" <<'PY'
import pathlib,sys
key=pathlib.Path(sys.argv[1]).read_text().strip()
if not key.startswith('ssh-ed25519 ') or '\n' in key: raise ValueError('Invalid SSH key')
p=pathlib.Path('/home/duckmoo-nexus-sync/.ssh/authorized_keys')
p.write_text('restrict,command="sudo -n /usr/bin/python3 /opt/duckmoo-nexus-clean/receiver.py" '+key+'\n')
p.chmod(0o600)
PY
chown duckmoo-nexus-sync:duckmoo-nexus-sync /home/duckmoo-nexus-sync/.ssh/authorized_keys
echo 'duckmoo-nexus-sync ALL=(root) NOPASSWD: /usr/bin/python3 /opt/duckmoo-nexus-clean/receiver.py' > /etc/sudoers.d/duckmoo-nexus-clean
# sudo must retain only the forced-command argument, never a client environment.
echo 'Defaults:duckmoo-nexus-sync env_keep += "SSH_ORIGINAL_COMMAND"' >> /etc/sudoers.d/duckmoo-nexus-clean
chmod 440 /etc/sudoers.d/duckmoo-nexus-clean
visudo -cf /etc/sudoers.d/duckmoo-nexus-clean
docker compose --project-directory "$target" build ingest
docker compose --project-directory "$target" up -d --wait postgres
docker compose --project-directory "$target" run --rm -T ingest init
docker compose --project-directory "$target" run --rm -T ingest restore
docker compose --project-directory "$target" up -d grafana
echo 'Server ready for source upload; installation is not yet complete.'
