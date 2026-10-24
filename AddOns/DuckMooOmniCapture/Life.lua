local _,O=...
-- A life starts when recording starts, never at an invented character creation time.
function O.Client()
 local _,_,_,interface=O.Call(GetBuildInfo)
 return type(interface)=="number" and interface>=16000 and interface<17000 and "forever" or "retail"
end
function O.Life()
 local c=O.Character();if not c then return nil,"unavailable" end
 if not c.life then c.life={id=c.journalID..":life:1",startedAt=GetServerTime(),startLevel=O.Call(UnitLevel,"player"),highestLevel=O.Call(UnitLevel,"player"),mode=O.Client()=="forever" and "unconfirmed" or "standard",modeSource="default",deaths=0,client=O.Client(),startMeaning="first_observed"} end
 local level=O.Call(UnitLevel,"player");if type(level)=="number" and level>0 and not c.life.endedAt then c.life.highestLevel=math.max(c.life.highestLevel or 0,level) end
 return c.life,"captured","Recording begins at first observation; Hardcore mode is explicitly configured, not inferred from a death."
end
function O.LifeMode(hardcore)
 local life=O.Life();if not life then return end
 local previous=life.mode;life.mode=hardcore and "hardcore" or "standard";life.modeSource="user";life.modeSetAt=GetServerTime()
 O.Event("life_mode",{previous=previous,mode=life.mode,source="user"});O.Store("life",life,"captured")
end
function O.Level(level)
 local life=O.Life();if not life then return end
 if type(level)=="number" then life.highestLevel=math.max(life.highestLevel or 0,level) end
 O.Event("level",{level=level});O.Store("life",life,"captured")
end
function O.Death()
 local c=O.Character();if not c or c.deathOpen then return end
 c.deathOpen=true
 local life=O.Life();life.deaths=(life.deaths or 0)+1;life.lastDeathAt=GetServerTime()
 if life.mode=="hardcore" and not life.endedAt then life.endedAt=life.lastDeathAt;life.endReason="observed_death" end
 -- No unrestricted combat-log stream or guessed killer attribution.
 O.Event("death",O.Profile());O.Store("life",life,"captured")
end
function O.EventContext(c)
 local s=c.sections.profile;local p=s and s.data or {}
 return {level=p.level,zone=p.zone,subzone=p.subzone,mapID=p.mapID,profileObservedAt=s and s.observedAt,client=O.Client()}
end
