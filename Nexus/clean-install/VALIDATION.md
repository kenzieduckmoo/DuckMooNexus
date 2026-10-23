# Release validation — 2026-10-20

- 17 automated tests passed: original parser/archive/market checks plus unified Journalator and backup collection, stable retry packets, missing-directory and invalid-source failures, and bound dashboard datasources.
- All PowerShell entrypoints parsed successfully. Running sync from a directory containing spaces resolved `config.json` beside the script, logged the missing configuration, and returned exit code 1.
- The invisible WScript launcher was executed against a child returning 7 and returned 7 itself.
- All 56 original historical snapshot manifests passed compressed-byte hash and length validation. Real data adapters parsed 19,897 Journalator records, 982 timestamped Warbank ledger points, 1,560,430 Auctionator observations, 195,087 TSM rows, and the complete DuckMooCapture source. See `real-data-verification.json`.
- Compose/provisioning YAML and dashboard JSON were parsed; dashboard datasource references resolve to the provisioned datasource.

The complete Ubuntu/Docker deployment has **not** been run here. This Windows environment has no Docker/PostgreSQL runtime. The server is reachable, but the available SSH key invokes the existing restricted receiver instead of an administrator shell. SQL execution, Docker image build, Grafana startup, and scheduled-task registration therefore remain live installation checks, performed automatically by `Install-Nexus.ps1`; they are not claimed as verified results.

The installer will not print successful completion unless PostgreSQL has real normalized records, both Grafana dashboard UIDs are provisioned, datasource connectivity passes, and Windows task registration succeeds.
