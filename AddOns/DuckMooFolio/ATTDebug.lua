local _,F=...
local M=F.Model
local function text(value)
    if value==nil then return 'nil' end
    if type(value)=='table' then
        local out={};for _,v in pairs(value)do if #out<20 then out[#out+1]=tostring(v)end end
        return table.concat(out,',')
    end
    return M.Display(value):gsub('[\r\n]',' ')
end
local function filter(fn,node)
    if type(fn)~='function' then return 'unavailable' end
    local ok,result=pcall(fn,node)
    return not ok and 'error' or result and 'pass' or 'fail'
end
function F.RecordQuestDebug(app,zone,node,status,path,reference,eligible,budget,frame)
    if status~='counted' and not budget.enabled then return end
    zone.questRows=zone.questRows or {}
    if #zone.questRows>=500 or budget.used>=8000 then zone.debugTruncated=(zone.debugTruncated or 0)+1;return end
    budget.used=budget.used+1
    local checked=status=='counted' or status=='duplicate' or status=='excluded: group filter'
    local row={questID=node.questID,name=F.ATTLabel(node) or ('Quest '..node.questID),status=status,
        objectKey=F.ReadATT(node,'key'),mountmodID=F.ReadATT(node,'mountmodID'),hiddenTracking=F.Clean(F.ReadATT(node,'isHQT')),
        groupFilter=checked and (eligible and 'pass' or 'fail') or 'not evaluated',
        path=path or (frame and F.ATTPath(frame)),reference=not not reference}
    if budget.enabled then
        budget.usedDetailed=true
        row.collected=F.Clean(F.ReadATT(node,'collected'));row.collectible=F.Clean(F.ReadATT(node,'collectible'));row.visible=F.Clean(F.ReadATT(node,'visible'));row.saved=F.Clean(F.ReadATT(node,'saved'))
        row.recursiveFilter=filter(app.RecursiveGroupRequirementsFilter,node)
        local filters=app.Modules and app.Modules.Filter and app.Modules.Filter.Filters or {}
        row.characterFilter=filter(filters.RecursiveCharacterRequirementsFilter,node)
        row.characterComplete=F.Safe(C_QuestLog and C_QuestLog.IsQuestFlaggedCompleted,node.questID)
        row.repeatable=F.Clean(F.ReadATT(node,'repeatable'));row.daily=F.Clean(F.ReadATT(node,'isDaily'));row.weekly=F.Clean(F.ReadATT(node,'isWeekly'))
        row.unobtainable=F.Clean(F.ReadATT(node,'u'));row.races=F.Clean(F.ReadATT(node,'races'));row.classes=F.Clean(F.ReadATT(node,'classes'))
    end
    zone.questRows[#zone.questRows+1]=row
end
function F.QuestReport(character,snapshot,zone)
    if zone.captureError then
        local e=zone.captureError;local context=e.context or {}
        return table.concat({"Character Folio ATT capture failure | addon "..text(e.addonVersion),
            'Character: '..text(character.name)..'-'..text(character.realm),
            'Failed at: '..date('%Y-%m-%d %H:%M:%S',e.seenAt)..' local | ATT '..text(e.attVersion),
            'Previous collection snapshot was retained. This does not establish that ATT is outdated.',
            'Stage: '..text(context.stage)..' | node '..text(context.visited)..' | questID '..text(context.questID)..' | instanceID '..text(context.instanceID),
            'ATT path: '..text(context.path),'','Error: '..text(e.message)},'\n')
    end
    local lines={"Character Folio ATT quest diagnostic | addon "..F.version,
        'Character: '..text(character.name)..'-'..text(character.realm),
        'Zone: '..text(zone.name)..' | mapID '..text(zone.mapID),
        'Capture: '..date('%Y-%m-%d %H:%M:%S',snapshot.seenAt)..' local | ATT '..text(snapshot.attVersion),
        'Captured ATT mode: '..text(snapshot.mode),
        'Collector count: '..text(zone.missing)..' distinct quest IDs | detailed debug: '..text(snapshot.questDebug),
        'ATT zone/quest windows use CURRENT filters; this report uses the SAVED capture.',
        'Only visited branches are listed. Invisible parent branches are not traversed.',
        'Only actual ATT Quest objects count; mount unlock flags and hidden tracking quests do not. Duplicate IDs count once.',
        'ATT profile filters decide eligibility; the separate current-character check is diagnostic only.',
        'A recursive-filter failure on a counted quest is a possible mismatch, not proof that the quest is obtainable.',
        ''}
    if snapshot.questDebugStopped then lines[#lines+1]='Extra debug was switched OFF during this scan. Earlier detailed rows are retained; later rows use normal diagnostics.'end
    if snapshot.scan then local s=snapshot.scan;lines[#lines+1]=string.format('Scan: %d nodes, %d batches, %.2fs elapsed, %d instance loot branches skipped.',s.nodes,s.batches,s.elapsedSeconds,s.prunedInstances)end
    if not zone.questRows then lines[#lines+1]='This older snapshot has no quest details. Enable /folio att debug on, then Refresh on this character.' end
    for _,row in ipairs(zone.questRows or {})do
        lines[#lines+1]=text(row.status)..' | '..text(row.questID)..' | '..text(row.name)
        lines[#lines+1]='  objectKey='..text(row.objectKey)..' mountmodID='..text(row.mountmodID)..' hiddenTracking='..text(row.hiddenTracking)
        lines[#lines+1]='  collected='..text(row.collected)..' collectible='..text(row.collectible)..' visible='..text(row.visible)..' saved='..text(row.saved)..' groupFilter='..text(row.groupFilter)..' reference='..text(row.reference)
        lines[#lines+1]='  recursiveFilter='..text(row.recursiveFilter)..' characterFilter='..text(row.characterFilter)..' characterComplete='..text(row.characterComplete)
        if snapshot.questDebug then lines[#lines+1]='  repeatable='..text(row.repeatable)..' daily='..text(row.daily)..' weekly='..text(row.weekly)..' unobtainable='..text(row.unobtainable)..' races='..text(row.races)..' classes='..text(row.classes)end
        lines[#lines+1]='  ATT path: '..text(row.path)
    end
    if zone.debugTruncated then lines[#lines+1]='LIMIT: '..zone.debugTruncated..' additional diagnostic rows omitted (500 per zone / 8000 per capture). The zone count is not capped.' end
    lines[#lines+1]='';lines[#lines+1]='Compare a specific ID with /folio att quest ID. Copy this report with Ctrl+A, Ctrl+C.'
    return table.concat(lines,'\n')
end
function F.OpenATTZone(mapID)
    local app=_G.AllTheThings
    if F.Safe(InCombatLockdown)then return false end
    if type(app)=='table' and type(app.ToggleMiniListForCurrentZone)=='function' then return pcall(app.ToggleMiniListForCurrentZone,mapID)end
    return false
end
function F.OpenATTQuest(id)
    local app=_G.AllTheThings;id=tonumber(id)
    if not id or id<=0 or id%1~=0 or F.Safe(InCombatLockdown)then return false end
    if type(app)=='table' and type(app.CreatePopoutForSearch)=='function' then local ok,opened=pcall(app.CreatePopoutForSearch,'questID:'..id);return ok and opened==true end
    return false
end
function F.ShowQuestDebug(zone,character,snapshot)
    if F.Safe(InCombatLockdown)then return end
    local panel=F.questDebugFrame
    if not panel then
        panel=CreateFrame('Frame','DuckMooFolioQuestDebug',UIParent,'BackdropTemplate');F.questDebugFrame=panel
        panel:SetSize(660,480);panel:SetPoint('CENTER');panel:SetFrameStrata('DIALOG');panel:SetClampedToScreen(true);panel:EnableMouse(true);panel:SetMovable(true);panel:RegisterForDrag('LeftButton')
        panel:SetScript('OnDragStart',function(self)self:StartMoving()end);panel:SetScript('OnDragStop',function(self)self:StopMovingOrSizing()end)
        panel:SetBackdrop({bgFile='Interface/Buttons/WHITE8X8',edgeFile='Interface/Buttons/WHITE8X8',edgeSize=1});panel:SetBackdropColor(.025,.02,.035,1);panel:SetBackdropBorderColor(.25,.15,.32,1)
        table.insert(UISpecialFrames,'DuckMooFolioQuestDebug')
        local title=panel:CreateFontString(nil,'OVERLAY','GameFontNormal');title:SetPoint('TOPLEFT',12,-12);title:SetText('Quest count diagnostics');title:SetTextColor(1,1,1)
        local function button(caption,x,width,callback)
            local b=CreateFrame('Button',nil,panel,'UIPanelButtonTemplate');b:SetSize(width,23);b:SetPoint('TOPRIGHT',x,-7);b:SetText(caption);b:SetScript('OnClick',callback);return b
        end
        button('X',-7,24,function()panel:Hide()end)
        panel.openZone=button('Open zone in ATT',-37,145,function()if not panel.mapID or not F.OpenATTZone(panel.mapID)then panel.hint:SetText('ATT zone window unavailable, or you are in combat. The report is still available.')end end)
        button('Copy report',-188,105,function()panel.edit:SetFocus();panel.edit:HighlightText()end)
        local scroll=CreateFrame('ScrollFrame',nil,panel,'UIPanelScrollFrameTemplate');panel.scroll=scroll;scroll:SetPoint('TOPLEFT',12,-42);scroll:SetPoint('BOTTOMRIGHT',-30,35)
        local edit=CreateFrame('EditBox',nil,scroll);panel.edit=edit;edit:SetMultiLine(true);edit:SetAutoFocus(false);edit:SetFontObject('GameFontHighlightSmall');edit:SetTextColor(1,1,1);edit:SetWidth(604);scroll:SetScrollChild(edit)
        edit:SetScript('OnEscapePressed',function()edit:ClearFocus();panel:Hide()end)
        edit:SetScript('OnTextChanged',function(self,user)if user then self:SetText(self.report or '')end end)
        panel.hint=panel:CreateFontString(nil,'OVERLAY','GameFontHighlightSmall');panel.hint:SetPoint('BOTTOMLEFT',12,12);panel.hint:SetWidth(630);panel.hint:SetJustifyH('LEFT');panel.hint:SetTextColor(1,.87,.32)
    end
    local report=F.QuestReport(character,snapshot,zone);panel.mapID=zone.mapID;panel.edit.report=report;panel.edit:SetText(report)
    panel.openZone:SetEnabled(zone.mapID~=nil)
    local _,lines=report:gsub('\n','\n');panel.edit:SetHeight(math.max(390,(lines+2)*15));panel.scroll:SetVerticalScroll(0)
    panel.hint:SetText('For deeper capture: /folio att debug on, then Refresh. Copy report selects text; press Ctrl+C.');panel:Show()
end
function F.ShowCaptureError()
    local c=F.db.characters[F.current];local err=c and c.captureError
    if not err then print('Folio ATT: No capture failure recorded by this version. Click Refresh to retry.');return end
    F.ShowQuestDebug({captureError=err},c,c.att or {})
end
function F.ChooseQuestDebug(query)
    local c=F.db.characters[F.selected or F.current];local snapshot=c and c.att
    if not snapshot then return end
    local options={}
    for _,zone in ipairs(snapshot.zones or {})do
        if query and (tonumber(query)==zone.mapID or text(zone.name):lower()==query:lower())then F.ShowQuestDebug(zone,c,snapshot);return end
        options[#options+1]={id=zone.mapID,name=zone.name..' ('..zone.missing..')'}
    end
    F.Choose('Quest diagnostics: choose a zone',options,function(id)for _,zone in ipairs(snapshot.zones)do if zone.mapID==id then F.ShowQuestDebug(zone,c,snapshot);return end end end)
end
