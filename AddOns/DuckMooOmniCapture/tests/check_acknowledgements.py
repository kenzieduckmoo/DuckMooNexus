"""One receipt round trip: synthetic archive -> generated Lua -> bounded prune."""
from pathlib import Path
import gzip,json,sys,tempfile,zipfile
ROOT=Path(__file__).resolve().parents[1]
WORKSPACE=ROOT.parent.parent
sys.path.insert(0,str(WORKSPACE/'Nexus/test-deps'))
sys.path.insert(0,str(WORKSPACE/'Nexus/clean-install/app'))
from lupa.lua51 import LuaRuntime
from write_omni_ack import publish,acknowledgement_rows

with tempfile.TemporaryDirectory(dir=WORKSPACE/'Nexus') as folder:
    root=Path(folder);sv=root/'client/WTF/Account/FIXTURE/SavedVariables';sv.mkdir(parents=True)
    addon=root/'client/Interface/AddOns/DuckMooOmniCapture';addon.mkdir(parents=True)
    (addon/'DuckMooOmniCapture.toc').write_text('Acknowledgements.lua\n',encoding='utf-8')
    state=root/'state';(state/'packets').mkdir(parents=True)
    digest='a'*64
    data='''DuckMooOmniCaptureDB = {
 ["schema"] = 1,
 ["characters"] = {
  ["Player-104-ABCD"] = {
   ["journalID"] = "fixture:123",
   ["sequence"] = 2,
   ["events"] = {
    { ["id"] = 1, ["at"] = 100, },
    { ["id"] = 2, ["at"] = 101, },
   },
  },
 },
}
'''
    # The SavedVariables reader deliberately accepts multiline assignments only.
    data=data.replace('{ ["id"] = 1, ["at"] = 100, },','{\n ["id"] = 1,\n ["at"] = 100,\n },').replace('{ ["id"] = 2, ["at"] = 101, },','{\n ["id"] = 2,\n ["at"] = 101,\n },')
    manifest={'namespace':'retail-main-account','source':'DuckMooOmniCapture.lua','original_name':'DuckMooOmniCapture.lua','raw_bytes':len(data.encode())}
    with zipfile.ZipFile(state/'packets'/(digest+'.bundle'),'w') as z:
        z.writestr('manifest.json',json.dumps(manifest));z.writestr('source.lua.gz',gzip.compress(data.encode()))
    (state/'source-checkpoints.json').write_text(json.dumps({str(sv/'DuckMooOmniCapture.lua'):{'packet':digest}}))
    (state/'omni-committed-packets.json').write_text('[]')
    assert publish(sv,state)['status']=='awaiting_confirmed_archive'
    assert not (addon/'Acknowledgements.lua').exists()
    (state/'omni-committed-packets.json').write_text(json.dumps([digest]))
    # A newer live file must never be mistaken for the confirmed archive.
    (sv/'DuckMooOmniCapture.lua').write_text('UNCONFIRMED LIVE CONTENT')
    assert publish(sv,state)=={'status':'published','journals':1}
    assert publish(sv,state)['status']=='unchanged'
    lua=LuaRuntime(unpack_returned_tuples=True)
    lua.execute('O={};function GetServerTime() return 105 end')
    lua.execute('assert(loadstring(...))("DuckMooOmniCapture",O)',(ROOT/'Model.lua').read_text())
    lua.execute('assert(loadstring(...))("DuckMooOmniCapture",O)',(addon/'Acknowledgements.lua').read_text())
    lua.execute('''
    local guid='Player-104-ABCD'
    local c={journalID='fixture:123',sequence=3,events={{id=1,at=100},{id=2,at=101},{id=3,at=102}}}
    local receipt=O.acknowledgements.characters[guid]
    receipt.journalID='older-history';O.PrepareJournal(guid,c);assert(#c.events==3)
    receipt.journalID='fixture:123';receipt.at=999;O.PrepareJournal(guid,c);assert(#c.events==3)
    receipt.at=101;receipt.through=4;O.PrepareJournal(guid,c);assert(#c.events==3)
    receipt.through=2;O.PrepareJournal(guid,c)
    assert(#c.events==1 and c.events[1].id==3 and c.sequence==3 and c.archivedEvents==2)
    O.PrepareJournal(guid,c);assert(c.archivedEvents==2 and #c.events==1)
    ''')
    assert (sv/'DuckMooOmniCapture.lua').read_text()=='UNCONFIRMED LIVE CONTENT'

assert acknowledgement_rows({'schema':1,'characters':{'Player-104-ABCD':{'events':[]}}})=={}
try:acknowledgement_rows({'schema':1,'characters':{'Player-104-ABCD':{'journalID':'fixture','sequence':3,'events':[{'id':1,'at':100},{'id':3,'at':102}]}}})
except ValueError:pass
else:raise AssertionError('Journal gap accepted')
print('Confirmed archive -> Lua receipt -> prefix rotation passed; unconfirmed, stale, mismatched and gap cases retain events.')
