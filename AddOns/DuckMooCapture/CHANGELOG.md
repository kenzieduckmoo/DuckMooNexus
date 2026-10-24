# 0.9.0

- Scan whole quantities at each available reagent quality instead of splitting a slot into mixed-quality allocations.
- Combine whole-slot choices across distinct required slots, retaining the cap, both concentration modes and pause/resume safeguards.
- Advance the persistent scanner cache revision so older mixed-allocation jobs are not resumed.
- Preserve original SavedVariables/archives and manual mixed-reagent captures. Update the bundled guide.
- Focused Lua 5.1 checks pass; actual in-game timing remains unmeasured.

