local _,F=...
local function position()
    local angle=math.rad(F.db.settings.minimapAngle or 190)
    local radius=(Minimap:GetWidth() or 140)/2+7
    local x,y=math.cos(angle),math.sin(angle)
    if GetMinimapShape and GetMinimapShape()=='SQUARE' then
        local scale=math.max(math.abs(x),math.abs(y));x,y=x/scale,y/scale
    end
    F.minimap:ClearAllPoints();F.minimap:SetPoint('CENTER',Minimap,'CENTER',x*radius,y*radius)
end
function F.CreateMinimap()
    if not Minimap or not F.db then return end
    if not F.minimap then
        local b=CreateFrame('Button','DuckMooFolioMinimapButton',Minimap);F.minimap=b
        b:SetSize(32,32);b:SetFrameStrata('MEDIUM');b:SetFrameLevel(Minimap:GetFrameLevel()+5)
        local icon=b:CreateTexture(nil,'ARTWORK');icon:SetTexture('Interface/Icons/INV_Misc_Book_09');icon:SetAllPoints()
        b:SetHighlightTexture('Interface/Minimap/UI-Minimap-ZoomButton-Highlight')
        b:RegisterForClicks('LeftButtonUp','RightButtonUp');b:RegisterForDrag('LeftButton')
        b:SetScript('OnClick',function(_,mouse)
            if F.minimapDragged then return end
            if mouse=='RightButton' then F.Show('settings')
            elseif F.frame and F.frame:IsShown() then F.frame:Hide() else F.Show() end
        end)
        b:SetScript('OnDragStart',function(self)
            F.minimapDragged=true
            self:SetScript('OnUpdate',function()
                local cx,cy=Minimap:GetCenter();local mx,my=GetCursorPosition();local scale=Minimap:GetEffectiveScale()
                F.db.settings.minimapAngle=math.deg(math.atan2(my/scale-cy,mx/scale-cx));position()
            end)
        end)
        b:SetScript('OnDragStop',function(self)
            self:SetScript('OnUpdate',nil);position()
            C_Timer.After(.15,function() F.minimapDragged=false end)
        end)
        b:SetScript('OnEnter',function(self)
            GameTooltip:SetOwner(self,'ANCHOR_LEFT');GameTooltip:SetText('DuckMoo Services: Character Folio')
            GameTooltip:AddLine('Left-click: open / close',1,1,1)
            GameTooltip:AddLine('Right-click: settings',1,1,1)
            GameTooltip:AddLine('Drag around the minimap. Your alt army awaits.',.75,.6,1,true);GameTooltip:Show()
        end)
        b:SetScript('OnLeave',function() GameTooltip:Hide() end)
    end
    position();F.minimap:SetShown(not F.db.settings.hideMinimap)
end
