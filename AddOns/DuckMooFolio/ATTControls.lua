local _,F=...
function F.CancelATT()
    if F.attRun then F.attRun.cancelled=true end
    F.attRun=nil;F.attBusy=false;F.activeQuestDebug=nil
    F.attMessage='Scan stopped. Previous snapshot retained; click Refresh to try again.'
    F.DrawIfShown()
end
function F.RefreshATTControl()
    if F.attBusy then F.CancelATT()else F.RefreshATT()end
end
function F.SetQuestDebug(enabled)
    F.db.settings.questDebug=not not enabled
    if not enabled and F.activeQuestDebug and F.activeQuestDebug.enabled then F.activeQuestDebug.enabled=false;F.activeQuestDebug.stopped=true end
end
function F.ATTStats()
    if F.attBusy then local r=F.attRun or {};F.Print(string.format('ATT scan running: %d nodes, %d branches queued, %.1fs elapsed. /folio att cancel keeps the previous snapshot.',r.nodes or 0,r.pending or 0,r.elapsed or 0));return end
    local c=F.db.characters[F.selected or F.current];local s=c and c.att and c.att.scan
    if s then F.Print(string.format('ATT last scan: %d nodes, %d batches, %.2fs elapsed, %d instance loot branches skipped. Detailed debug %s.',s.nodes,s.batches,s.elapsedSeconds,s.prunedInstances,s.detailedDebug and 'captured' or 'off'))
    else F.Print('Refresh Collection leads once to record scan timings.')end
end
function F.ATTCommand(command)
    command=(command or ''):lower():match('^%s*(.-)%s*$')
    if command=='version' then F.Print('Loaded runtime '..F.version..'. Reload WoW after updating files.')
    elseif command=='cancel' then F.CancelATT()
    elseif command=='stats' then F.ATTStats()
    elseif command=='debug' or command:match('^debug%s')then
        local value=command:match('^debug%s*(.*)$');local enabled
        if value=='on' then enabled=true elseif value=='off' then enabled=false elseif value=='' then enabled=not F.db.settings.questDebug else F.Print('/folio att debug on or /folio att debug off');return end
        F.SetQuestDebug(enabled);F.Print('ATT debug '..(enabled and 'ON. Refresh for extra diagnostics.' or 'OFF. Extra diagnostics stopped; saved reports retained.'));F.DrawIfShown()
    elseif command=='error' then if F.DebugReady()then F.ShowCaptureError()end
    elseif command=='quests' or command:match('^quests%s')then if F.DebugReady()then F.Show('att');F.ChooseQuestDebug(command:match('^quests%s+(.+)$'))end
    elseif command:match('^quest%s')then if F.DebugReady() and not F.OpenATTQuest(command:match('^quest%s+(%d+)$'))then F.Print('ATT quest window unavailable. Use /folio att quest ID outside combat.')end
    elseif command=='refresh' then
        if F.attBusy then F.CancelATT()else F.Show('att');F.RefreshATT()end
    elseif command=='' then F.Show('att')
    else F.Print('/folio att refresh | cancel | stats | version | debug on/off | quests [zone/mapID] | quest ID | error')end
end
