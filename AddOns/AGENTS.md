# DuckMoo addon conventions

- Every existing and future DuckMoo addon TOC, including client-specific TOC variants, must contain exactly `## Category: DuckMoo Media`.
- General character/activity omni-capture must be separate from the crafting data capture addon (DuckMooCapture). Use its own addon folder, SavedVariables, settings and capture lifecycle; either collector must be independently enableable and disableable.
- Client-specific variants or multiple omni-capture addons are acceptable when compatibility requires them. Do not make general activity recording depend on the crafting scanner.
- Separate collectors may feed the same Nexus PostgreSQL database and share read-only character identity/context. Preserve source/client provenance and independent collection behavior.
- Apply these conventions to DuckMoo-owned addons, not third-party addons. Preserve existing SavedVariables, notes, tags and client interface metadata when making unrelated changes.
