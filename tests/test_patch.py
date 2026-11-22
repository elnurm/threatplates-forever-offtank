from pathlib import Path
import sys

from lupa.lua51 import LuaRuntime

lua = LuaRuntime(unpack_returned_tuples=True)
base = Path(__file__).resolve().parents[1]
for rel in ('Modules/Threat.lua', 'Options.lua'):
    lua.execute('assert(loadstring(...))', (base / 'TidyPlates_ThreatPlates' / rel).read_text(encoding='utf-8'))

lua.execute('''
secret = setmetatable({}, {
  __lt = function() error("Compared secret") end,
  __le = function() error("Compared secret") end,
  __concat = function() error("Concatenated secret") end
})
function issecretvalue(v) return rawequal(v, secret) end
statuses = {}; roles = {}; assignments = {}; identities = {}; exists = {}
raid = true; count = 2; playerRole = "tank"
function IsInRaid() return raid end
function GetNumGroupMembers() return count end
function GetNumSubgroupMembers() return count end
function UnitIsUnit(a, b) return identities[b] end
function UnitExists(u) if exists[u] ~= nil then return exists[u] end return true end
function UnitGroupRolesAssigned(u) return roles[u] end
function GetPartyAssignment(_, u) return assignments[u] end
function UnitThreatSituation(u, mob) return statuses[u] end
function UnitAffectingCombat() return true end
function UnitIsPlayer() return true end
function UnitPlayerControlled() return true end
function IsInInstance() return true end
function InCombatLockdown() return true end
Addon = {
  IS_FOREVER = true, HAS_MIDNIGHT_API = true, ExpansionIsAtLeastMists = false,
  Threat = {}, THREAT_REFERENCE = {[0]="LOW", [1]="MEDIUM", [2]="HIGH", [3]="HIGH"},
  GetPlayerRole = function() return playerRole end,
  EventService = {Subscribe=function() end, Publish=function() end, Unsubscribe=function() end},
  Style = {Update=function() end},
  db = {profile = {threat = {toggle = {OffTank=true}, UseThreatTable=true}}}
}
frame = {unit = {unitid="nameplate1"}}
function Addon:GetActiveThreatPlates() return pairs({nameplate1=frame}) end
function reset()
  statuses={player=0, raid2=3}; roles={raid2="TANK"}; assignments={};
  identities={raid1=true, raid2=false}; exists={}; raid=true; count=2; playerRole="tank"
  Addon.IS_FOREVER=true; Addon.HAS_MIDNIGHT_API=true
  Addon.db.profile.threat.toggle.OffTank=true
  frame.unit={unitid="nameplate1"}
end
''')
lua.execute((base / 'TidyPlates_ThreatPlates/Modules/Threat.lua').read_text(), 'TidyPlates_ThreatPlates', lua.globals().Addon)
cases = [
    ('other tank secure', '', 'OFFTANK'),
    ('other tank insecure', 'statuses.raid2=2', 'OFFTANK'),
    ('other tank lost threat', 'statuses.raid2=1', 'LOW'),
    ('secret other threat', 'statuses.raid2=secret', 'LOW'),
    ('missing other threat', 'statuses.raid2=nil', 'LOW'),
    ('player has aggro', 'statuses.player=3', 'HIGH'),
    ('player not on threat table', 'statuses.player=nil', 'OFFTANK'),
    ('player threat secret', 'statuses.player=secret', None),
    ('dps has aggro', 'roles.raid2="DAMAGER"', 'LOW'),
    ('main tank assignment', 'roles.raid2="NONE"; assignments.raid2=true', 'OFFTANK'),
    ('secret role and assignment', 'roles.raid2=secret; assignments.raid2=secret', 'LOW'),
    ('secret identity', 'identities.raid2=secret', 'LOW'),
    ('secret existence', 'exists.raid2=secret', 'LOW'),
    ('missing member', 'exists.raid2=false', 'LOW'),
    ('not tank role', 'playerRole="dps"', 'LOW'),
    ('disabled setting', 'Addon.db.profile.threat.toggle.OffTank=false', 'LOW'),
    ('solo', 'raid=false; count=0', 'LOW'),
    ('party tank', 'raid=false; count=1; roles.party1="TANK"; statuses.party1=3; identities.party1=false', 'OFFTANK'),
    ('midnight unchanged', 'Addon.IS_FOREVER=false', 'LOW'),
]
for name, setup, expected in cases:
    lua.execute('reset()\n' + setup + '\nAddon.Threat.UpdateSettings(); Addon.Threat.SetUnitAttribute(frame.unit)')
    actual = lua.globals().frame.unit.ThreatLevel
    assert actual == expected, (name, actual, expected)
lua.execute('''
reset(); Addon.Threat.UpdateSettings(); Addon.Threat.SetUnitAttribute(frame.unit)
assert(frame.unit.IsOfftanked == true)
statuses.raid2=secret; Addon.Threat.Update(frame)
assert(frame.unit.IsOfftanked == false and frame.unit.ThreatLevel == "LOW")
statuses.raid2=3; Addon.Threat.Update(frame)
assert(frame.unit.IsOfftanked == true)
Addon.Threat.LeavingCombat()
assert(frame.unit.IsOfftanked == false and frame.unit.ThreatLevel == nil)
''')
print(f'PASS: Lua 5.1 syntax for both files; {len(cases)} behavior cases; stale-state and leaving-combat checks.')
