# Threat Plates: Forever off-tank patch

An experimental patch for **Threat Plates 13.3.9 on WoW Forever** that restores
the separate nameplate color for mobs tanked by another tank when the game
exposes readable threat information.

**Reported working in-game by the initial tester.** This is a community patch,
not an official Threat Plates release, and is not confirmed for every encounter.

## Download and install

1. Install **Threat Plates 13.3.9** first from the
   [official addon page](https://www.curseforge.com/wow/addons/tidy-plates-threat-plates).
   This download contains only two replacement files, not the complete addon.
2. [Download the patch ZIP](https://github.com/elnurm/threatplates-forever-offtank/releases/latest/download/ThreatPlates-Forever-OffTank-v0.2.0.zip).
3. Back up `Modules/Threat.lua` and `Options.lua` inside your existing
   `_forever_/Interface/AddOns/TidyPlates_ThreatPlates/` folder.
4. Extract the ZIP and copy its `TidyPlates_ThreatPlates` folder into
   `_forever_/Interface/AddOns/`, merging the folder and replacing the two files.
   Keep all the other files in your existing addon folder.
5. Run `/reload`, then `/tptp`. Under **Threat System → Special Effects**, enable
   **Highlight Mobs on Off-Tanks**.
6. Use tank mode and ensure your co-tank has the **Tank role** or **Main Tank raid
   assignment**. Choose the **Off-Tank** color you prefer; gray is optional.

Test with a taunt swap: let the co-tank hold the mob, taunt it yourself, and have
the co-tank taunt it back. The off-tank color should follow readable tank threat.

## What changes

- Caches assigned tanks on Forever. Roster/role changes, world entry, combat
  entry, and settings updates rebuild the list. Per-mob threat updates visit
  only cached tanks, without repeating roster scans or role/assignment queries.
- Queries known raid/party members instead of relying on the enemy's target.
- Accepts Tank roles or Main Tank assignments.
- Applies the off-tank state only when another tank has readable threat status
  2 or 3. Skips secret or missing data and clears stale off-tank state.
- Restores the off-tank checkbox on Forever. Keeps the old threat heuristic disabled.
- Does not change saved profiles or color preferences.

If Blizzard hides the required information, this patch cannot reveal it and the
ordinary threat display remains. Addon updates can overwrite the patch. **Do not
apply these replacement files to another version without reviewing the changes.**

## Restore the original addon

Restore your two backed-up files, then `/reload`. Alternatively, reinstall the
official matching addon version. There is no need to delete your saved settings.

## Validation and source

Both edited files compile under Lua 5.1. The mocked tests cover 19 cases plus
stale-state and combat-exit checks. Additional tests cover cache invalidation,
role changes, reused raid tokens, group transitions, and disable/re-enable.
A 40-member mock raid with two other tanks performs zero role/assignment queries
and 2,000 other-tank threat queries over 1,000 updates. This verifies call counts,
not live-raid CPU time or FPS gains. Real Blizzard secret values are not fully
reproduced by these tests; encounter testing is still needed.

The replacement Lua files are included, and `offtank.patch` shows the changes
relative to the local 13.3.9 installation used for this patch. Run the tests with
Python and `lupa` installed: `python tests/test_patch.py`.

## Credits and license

Threat Plates is created and maintained by its original authors and contributors,
including Suicidal Katt and Backupiseasy. See the
[upstream repository](https://github.com/Backupiseasy/ThreatPlates).
The addon is listed as GPLv3 on its official CurseForge page. These modified files
are distributed under GNU GPL v3; see `LICENSE`. Changes made on 2026-11-22:
Forever-only guarded off-tank detection and restored configuration control.
Updated 2026-11-25 (v0.2.0): event-driven tank cache and cache lifecycle tests.

The approach was informed by [Plater's group-tank detection](https://github.com/Tercioo/Plater-Nameplates/blob/master/Plater.lua).
This repository is not affiliated with either upstream project.
