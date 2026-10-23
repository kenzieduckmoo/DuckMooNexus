local _,P=...
local function position()
    local angle=math.rad(P.db.settings.minimapAngle or 225)
    local radius=(Minimap:GetWidth() or 140)/2+7
    local x,y=math.cos(angle),math.sin(angle)
    if GetMinimapShape and GetMinimapShape()=='SQUARE' then
        local scale=math.max(math.abs(x),math.abs(y));x,y=x/scale,y/scale
    end
    P.minimap:ClearAllPoints();P.minimap:SetPoint('CENTER',Minimap,'CENTER',x*radius,y*radius)
end
function P.CreateMinimap()
    if not Minimap or not P.db then return end
    if not P.minimap then
        local b=CreateFrame('Button','DuckMooPlannerMinimapButton',Minimap);P.minimap=b
        b:SetSize(32,32);b:SetFrameStrata('MEDIUM');b:SetFrameLevel(Minimap:GetFrameLevel()+5)
        local icon=b:CreateTexture(nil,'ARTWORK');icon:SetTexture('Interface/AddOns/DuckMooPlanner/Media/Minimap.tga');icon:SetAllPoints()
        b:SetHighlightTexture('Interface/Minimap/UI-Minimap-ZoomButton-Highlight')
        b:RegisterForClicks('LeftButtonUp','RightButtonUp');b:RegisterForDrag('LeftButton')
        b:SetScript('OnClick',function(_,mouse)
            if P.minimapDragged then return end
            if mouse=='RightButton' then P.Show('settings')
            elseif IsShiftKeyDown and IsShiftKeyDown() then P.Show();P.SetCompact(not P.db.settings.compact)
            elseif P.frame and P.frame:IsShown() then P.frame:Hide() else P.Show() end
        end)
        b:SetScript('OnDragStart',function(self)
            P.minimapDragged=true
            self:SetScript('OnUpdate',function()
                local cx,cy=Minimap:GetCenter();local mx,my=GetCursorPosition();local scale=Minimap:GetEffectiveScale()
                P.db.settings.minimapAngle=math.deg(math.atan2(my/scale-cy,mx/scale-cx));position()
            end)
        end)
        b:SetScript('OnDragStop',function(self)
            self:SetScript('OnUpdate',nil);position()
            C_Timer.After(.15,function() P.minimapDragged=false end)
        end)
        b:SetScript('OnEnter',function(self)
            GameTooltip:SetOwner(self,'ANCHOR_LEFT');GameTooltip:SetText(P.fullName)
            GameTooltip:AddLine('Left-click: open / close',1,1,1)
            GameTooltip:AddLine('Right-click: settings | Shift-click: compact mode',1,1,1)
            GameTooltip:AddLine('Drag around the minimap. Your alt army awaits.',.75,.6,1,true);GameTooltip:Show()
        end)
        b:SetScript('OnLeave',function() GameTooltip:Hide() end)
    end
    position();P.minimap:SetShown(not P.db.settings.hideMinimap)
end
