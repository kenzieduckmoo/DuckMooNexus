# GitHub source upload — October 23, 2026

Repository: https://github.com/kenzieduckmoo/DuckMooNexus (private).

Initial source import commit: d8d1c694c20c4335f7bff80607209dec4d1e1fb3. Preserved parent initial commit 3a0a5dbb4db0a87900eac2430799d8d8d97a650b. Uploaded 323 source/documentation/required-asset files, about 4.8 MB. Runtime credentials, original SavedVariables/source archives, generated crafting data/plans, logs, installed dependencies, screenshots and generated release packages were excluded.

The source-only local working copy is `DuckMooNexus/`. It was published through the connected GitHub tools because command-line Git has no authenticated login. This folder is not an authenticated Git clone. Maintained development sources remain in the original `Nexus`, `CraftingDesk` and `AddOns` directories. Later edits must be reconciled into the source working copy and committed to GitHub as well.

The remote contains the native website, server/importers/SQL/Grafana sources, current timers, crafting engine and shared CraftingDesk, five DuckMoo addon sources, required decoder libraries/licenses and dated project notes. A new root README distinguishes current delivery from historical installer behavior. `tools/prepare-stack.py` assembles the separated sources into the existing server layout without deploying or copying private runtime data.

Source staging helpers are local at `Nexus/stage-github-source.py` and `Nexus/github-source-payload.py`. Preserve manually added root documentation/tools and source-only exclusions when staging again. The GitHub tree was read back to verify required source paths and file count. No application tests were rerun just for the upload; source assembly and disclosure exclusions were checked.
