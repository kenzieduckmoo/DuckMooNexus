local _, F = ...
local M=F.Model
local S=F.Safe
local unpack=unpack or table.unpack
F.TransFlag={{91/255,206/255,250/255},{245/255,169/255,184/255},{1,1,1},{245/255,169/255,184/255},{91/255,206/255,250/255}}
F.Themes={
 purple={name='DuckMoo Purple',bg={.065,.04,.09},panel={.105,.07,.14},button={.20,.12,.28},hover={.30,.19,.41},accent={.72,.45,1},text={.96,.92,1},muted={.73,.65,.83}},
 gunmetal={name='Gunmetal',bg={.075,.078,.11},panel={.13,.135,.18},button={.18,.18,.25},hover={.24,.23,.33},accent={.65,.53,.89},text={.94,.94,.98},muted={.69,.71,.80}},
 plum={name='Classic plum',bg={36/255,19/255,34/255},sidebar={50/255,27/255,48/255},panel={57/255,32/255,57/255},button={87/255,49/255,73/255},hover={115/255,65/255,94/255},accent={231/255,169/255,202/255},text={255/255,240/255,250/255},muted={226/255,195/255,216/255}},
 light={name='Light mode - warm pastels',bg={247/255,214/255,172/255},sidebar={241/255,195/255,173/255},panel={255/255,233/255,181/255},button={242/255,188/255,180/255},hover={227/255,173/255,203/255},accent={166/255,77/255,89/255},text={70/255,40/255,44/255},muted={89/255,57/255,61/255}},
 blizzard={name='Azeroth',bg={.055,.055,.06},panel={.10,.10,.11},button={.19,.15,.08},hover={.30,.24,.12},accent={.9,.72,.32},text={1,.94,.80},muted={.70,.66,.56}},
 trans={name='Trans pride',bg={91/255,206/255,250/255},sidebar={245/255,169/255,184/255},panel={245/255,169/255,184/255},button={91/255,206/255,250/255},hover={245/255,169/255,184/255},accent={255/255,255/255,255/255},text={14/255,19/255,31/255},muted={36/255,48/255,64/255},stripes=F.TransFlag},
 translight={name='Trans pride - dusk',bg={22/255,47/255,66/255},sidebar={64/255,38/255,54/255},panel={35/255,72/255,97/255},button={97/255,54/255,71/255},hover={117/255,66/255,86/255},accent={255/255,255/255,255/255},text={255/255,255/255,255/255},muted={226/255,211/255,222/255},stripes=F.TransFlag},
 lesbian={name='Lesbian pride',bg={.12,.055,.09},panel={.19,.075,.13},button={.32,.11,.22},hover={.43,.15,.30},accent={1,.54,.30},text={1,.94,.96},muted={.94,.65,.77},stripes={{.84,.18,.02},{1,.60,.32},{1,1,1},{.82,.38,.64},{.64,.02,.38}}},
 teal={name='Moonlit teal',bg={.035,.09,.10},panel={.055,.14,.16},button={.09,.24,.25},hover={.13,.32,.34},accent={.30,.85,.80},text={.90,1,.98},muted={.59,.78,.76}},
 crimson={name='Crimson',bg={.09,.03,.035},panel={.15,.045,.055},button={.26,.07,.10},hover={.37,.11,.14},accent={.94,.32,.40},text={1,.93,.92},muted={.81,.61,.61}},
 blue={name='Arcane blue',bg={.035,.055,.11},panel={.055,.085,.17},button={.09,.16,.30},hover={.14,.23,.40},accent={.39,.66,1},text={.94,.97,1},muted={.63,.73,.87}},
}
local function theme()return F.Themes[F.db and F.db.settings.theme or 'purple'] or F.Themes.purple end
F.themeTexts={};F.surfaces={}
function F.ApplyTheme()
 local t=theme();local alpha=F.db.settings.backgroundAlpha or .92
 for _,f in ipairs(F.surfaces)do
  local color=f._themeButton and (f._active and t.hover or t.button) or f._sidebar and (t.sidebar or t.panel) or f==F.frame and t.bg or t.panel
  f:SetBackdropColor(color[1],color[2],color[3],alpha)
  f:SetBackdropBorderColor(t.accent[1],t.accent[2],t.accent[3],f._active and 1 or 0)
 end
 for _,f in ipairs(F.themeTexts)do local color=f._fixedColor or (f._muted and t.muted or t.text);f:SetTextColor(color[1],color[2],color[3])end
 for _,input in pairs({F.rosterSearch,F.notePanel and F.notePanel.edit,F.tagPicker and F.tagPicker.input,F.choice and F.choice.search,F.viewEditor and F.viewEditor.edit})do input:SetTextColor(t.text[1],t.text[2],t.text[3])end
 if F.frame and F.frame.stripes then
  for i,texture in ipairs(F.frame.stripes)do
   local color=t.stripes and t.stripes[i] or t.accent
   texture:SetVertexColor(color[1],color[2],color[3],1)
   texture:SetShown(t.stripes~=nil or i==1)
  end
 end
end

-- WoW frames cannot be garbage collected. Recycle frames and font strings.
F.dynamicParents={}
local function acquire(parent,kind,template)
    if not F.dynamic then
        if kind=='FontString' then return parent:CreateFontString(nil,'OVERLAY',template) end
        return CreateFrame(kind,nil,parent,template)
    end
    if not parent._dmfPools then
        parent._dmfPools={};parent._dmfUsed={};F.dynamicParents[#F.dynamicParents+1]=parent
    end
    local key=kind..(template or '')
    local pool=parent._dmfPools[key] or {};parent._dmfPools[key]=pool
    local i=(parent._dmfUsed[key] or 0)+1;parent._dmfUsed[key]=i
    local f=pool[i]
    if not f then
        if kind=='FontString' then f=parent:CreateFontString(nil,'OVERLAY',template)
        else f=CreateFrame(kind,nil,parent,template) end
        pool[i]=f
    end
    f:ClearAllPoints();f:Show()
    return f
end
local function label(parent,text,x,y,width,font)
    local f=acquire(parent,'FontString',font or 'GameFontHighlight')
    f:SetFontObject(font or 'GameFontHighlight');f:SetHeight(0);f:SetWordWrap(true);
    if not f._themeText then f._themeText=true;F.themeTexts[#F.themeTexts+1]=f end
    f._fixedColor=nil;f._muted=(font=='GameFontDisableSmall');local color=f._muted and theme().muted or theme().text;f:SetTextColor(unpack(color));
    f:SetPoint('TOPLEFT',x,y); f:SetWidth(width); f:SetJustifyH('LEFT'); f:SetText(text)
    return f
end
local function roundSurface(f)
    if f._round then return end
    f._round={};F.surfaces[#F.surfaces+1]=f
    local radius=6
    local function texture()
        local t=f:CreateTexture(nil,'BACKGROUND');t:SetTexture('Interface/Buttons/WHITE8X8');f._round[#f._round+1]=t;return t
    end
    local center=texture();center:SetPoint('TOPLEFT',radius,-radius);center:SetPoint('BOTTOMRIGHT',-radius,radius)
    local top=texture();top:SetPoint('TOPLEFT',radius,0);top:SetPoint('TOPRIGHT',-radius,0);top:SetHeight(radius)
    local bottom=texture();bottom:SetPoint('BOTTOMLEFT',radius,0);bottom:SetPoint('BOTTOMRIGHT',-radius,0);bottom:SetHeight(radius)
    local left=texture();left:SetPoint('TOPLEFT',0,-radius);left:SetPoint('BOTTOMLEFT',0,radius);left:SetWidth(radius)
    local right=texture();right:SetPoint('TOPRIGHT',0,-radius);right:SetPoint('BOTTOMRIGHT',0,radius);right:SetWidth(radius)
    for _,c in ipairs({{'TOPLEFT',0,0,0,1,0,1},{'TOPRIGHT',0,0,1,0,0,1},{'BOTTOMLEFT',0,0,0,1,1,0},{'BOTTOMRIGHT',0,0,1,0,1,0}}) do
        local t=texture();t:SetTexture('Interface/AddOns/DuckMooFolio/Media/Corner.tga');t:SetSize(radius,radius);t:SetPoint(c[1],c[2],c[3]);t:SetTexCoord(c[4],c[5],c[6],c[7])
    end
    f:SetBackdrop(nil)
    f.SetBackdropColor=function(self,r,g,b,a)
        self._surfaceColor={r,g,b,a or 1}
        for _,t in ipairs(self._round) do t:SetVertexColor(r,g,b,a or 1) end
    end
    local accent=f:CreateTexture(nil,'BORDER');accent:SetTexture('Interface/Buttons/WHITE8X8');accent:SetWidth(2)
    accent:SetPoint('TOPLEFT',1,-6);accent:SetPoint('BOTTOMLEFT',1,6);f._accent=accent
    f.SetBackdropBorderColor=function(self,r,g,b,a) self._accent:SetVertexColor(r,g,b,a or 1) end
end
local function button(parent,text,x,y,width,action)
    local b=acquire(parent,'Button','BackdropTemplate');roundSurface(b);b._themeButton=true
    if not b._caption then
        b._caption=b:CreateFontString(nil,'OVERLAY','GameFontHighlightSmall');b._caption:SetPoint('CENTER');b:SetFontString(b._caption)
    end
    if not b._caption._themeText then b._caption._themeText=true;F.themeTexts[#F.themeTexts+1]=b._caption end
    b._active=false;b._caption:SetWidth(width-10);b._caption:SetWordWrap(false)
    b:SetSize(width,24);b:SetPoint('TOPLEFT',x,y);b:SetText(text);b:SetScript('OnClick',action)
    b:SetScript('OnMouseDown',function(self)local c=theme().hover;self:SetBackdropColor(c[1],c[2],c[3],F.db.settings.backgroundAlpha or .92)end)
    b:SetScript('OnMouseUp',function(self)local c=self._active and theme().hover or theme().button;self:SetBackdropColor(c[1],c[2],c[3],F.db.settings.backgroundAlpha or .92)end)
    b:SetBackdropColor(.18,.12,.26,.97);b:SetBackdropBorderColor(.50,.32,.70,0)
    b:SetScript('OnEnter',function(self)local c=theme().hover;self:SetBackdropColor(c[1],c[2],c[3],F.db.settings.backgroundAlpha or .92)end)
    b:SetScript('OnLeave',function(self)local c=self._active and theme().hover or theme().button;self:SetBackdropColor(c[1],c[2],c[3],F.db.settings.backgroundAlpha or .92)end)
    return b
end
local function panel(parent,name)
    local f=name and CreateFrame('Frame',name,parent,'BackdropTemplate') or acquire(parent,'Frame','BackdropTemplate')
    if parent==UIParent then
        -- Stack the entire window as one render group, including deep children.
        f:SetToplevel(true)
        f:SetFlattensRenderLayers(true)
    end
    roundSurface(f)
    if f.crest then f.crest:Hide() end;if f.bar then f.bar:Hide() end
    f:SetAlpha(1);f:EnableMouse(true);f:SetScript('OnMouseUp',nil);f:SetScript('OnEnter',nil);f:SetScript('OnLeave',nil)
    f:SetBackdropColor(.075,.052,.11,.98);f:SetBackdropBorderColor(.30,.22,.40,0)
    return f
end
local function tooltip(frame,title,lines)
    frame:SetScript('OnEnter',function(self)
        if self._caption then local c=theme().hover;self:SetBackdropColor(c[1],c[2],c[3],F.db.settings.backgroundAlpha or .92) end
        GameTooltip:SetOwner(self,'ANCHOR_RIGHT');GameTooltip:SetText(title)
        for _,s in ipairs(lines) do GameTooltip:AddLine(s,1,1,1,true) end
        GameTooltip:Show()
    end)
    frame:SetScript('OnLeave',function(self) if self._caption then local c=self._active and theme().hover or theme().button;self:SetBackdropColor(c[1],c[2],c[3],F.db.settings.backgroundAlpha or .92) end;GameTooltip:Hide() end)
end
local tabs={{'sheet','Character','CHARACTER'},{'notes','Notebook'},{'skills','Skills & trades'},{'reps','Reputations'},{'att','Collection leads'},{'roster','Roster','WARBAND'},{'census','Census'},{'settings','Preferences','PREFERENCES'}}
local function text(t,x,y,w,font) return label(F.content,M.Plain(t),x,-y,w,font) end
local function value(t) if t==nil then return 'Not recorded' end;return tostring(t) end
local function stamp(t) return t and date('%b %d, %Y %I:%M %p',t) or 'Not recorded' end
local function sorted(tableValue)
    local out={};for k,v in pairs(tableValue or {}) do out[#out+1]={id=k,value=v} end
    table.sort(out,function(a,b) return tostring(a.value.name or a.id)<tostring(b.value.name or b.id) end);return out
end
function F.Clear()
    for _,parent in ipairs(F.dynamicParents) do
        for _,pool in pairs(parent._dmfPools) do for _,f in ipairs(pool) do f:Hide() end end
        parent._dmfUsed={}
    end
end
local function card(x,y,w,h)
    local f=panel(F.content);f:SetPoint('TOPLEFT',x,-y);f:SetSize(w,h);return f
end
local function stat(x,y,w,title,content)
    local f=card(x,y,w,43)
    label(f,title:upper(),8,-5,w-16,'GameFontDisableSmall')
    label(f,M.Plain(value(content)),8,-20,w-16,'GameFontNormalLarge'):SetWordWrap(false)
    tooltip(f,title,{M.Plain(value(content))});return f
end
local function section(title,y)
    text(title:upper(),4,y,F.width-8,'GameFontNormal');return y+26
end
function F.Layout()
    local f=F.frame;if not f then return end
    F.width=math.max(700,f:GetWidth()-222);F.viewportHeight=math.max(280,f:GetHeight()-104)
    F.sidebar:ClearAllPoints();F.sidebar:SetPoint('TOPLEFT',12,-12);F.sidebar:SetSize(164,f:GetHeight()-24)
    F.scroll:ClearAllPoints();F.scroll:SetPoint('TOPLEFT',194,-84);F.scroll:SetSize(F.width,F.viewportHeight)
    F.content:SetWidth(F.width)
    F.pageTitle:SetWidth(F.width-264);F.pageContext:SetWidth(F.width-264)
    F.sideContext:ClearAllPoints();F.sideContext:SetPoint('BOTTOMLEFT',12,47)
    F.sideRealm:ClearAllPoints();F.sideRealm:SetPoint('BOTTOMLEFT',12,28)
    F.sideVersion:ClearAllPoints();F.sideVersion:SetPoint('BOTTOMLEFT',12,10)
    F.switchCharacter:ClearAllPoints();F.switchCharacter:SetPoint('BOTTOMLEFT',12,72)
end
function F.PickCharacter()
    local options={}
    for guid,c in pairs(F.db.characters)do options[#options+1]={id=guid,name=(c.name or '?')..' - '..(c.realm or '?')}end
    table.sort(options,function(a,b)return a.name<b.name end)
    F.Choose('Choose a character',options,function(guid)F.selected=guid;F.scroll:SetVerticalScroll(0);F.Render()end)
end
function F.CreateWindow()
    if F.frame then return end
    local f=panel(UIParent,'DuckMooFolioWindow');F.frame=f;table.insert(UISpecialFrames,'DuckMooFolioWindow')
    local size=F.db.settings.size or {1040,740}
    f:SetSize(math.min(math.max(940,size[1]),UIParent:GetWidth()-30),math.min(math.max(560,size[2]),UIParent:GetHeight()-30))
    f:SetPoint('CENTER');f:SetFrameStrata('HIGH')
    local p=F.db.settings.position
    if p then f:ClearAllPoints();f:SetPoint(p[1],UIParent,p[2],p[3],p[4])end
    f:SetMovable(true);f:EnableMouse(true)
    local drag=CreateFrame('Frame',nil,f);F.headerDrag=drag;drag:SetFrameLevel(f:GetFrameLevel()+1)
    drag:SetPoint('TOPLEFT',180,0);drag:SetPoint('TOPRIGHT',0,0);drag:SetHeight(70);drag:EnableMouse(true);drag:RegisterForDrag('LeftButton')
    drag:SetScript('OnDragStart',function()f:StartMoving()end)
    drag:SetScript('OnDragStop',function()f:StopMovingOrSizing();local a,_,b,x,y=f:GetPoint();F.db.settings.position={a,b,x,y}end)
    f:SetResizable(true);if f.SetResizeBounds then f:SetResizeBounds(940,560,1600,1100)end
    F.sidebar=panel(f);F.sidebar._sidebar=true
    f.stripes={}
    for i=1,5 do
        local t=F.sidebar:CreateTexture(nil,'ARTWORK');t:SetTexture('Interface/Buttons/WHITE8X8')
        t:SetPoint('TOPLEFT',12,-10-(i-1)*4);t:SetSize(140,4);f.stripes[i]=t
    end
    label(F.sidebar,'DuckMoo',12,-38,140,'GameFontNormalLarge')
    label(F.sidebar,'CHARACTER FOLIO',12,-59,140,'GameFontDisableSmall')
    F.tabButtons={};local y=86
    for _,tab in ipairs(tabs)do
        if tab[3] then label(F.sidebar,tab[3],12,-y,140,'GameFontDisableSmall');y=y+23 end
        local key=tab[1]
        local b=button(F.sidebar,tab[2],8,-y,148,function()
            if F.notePanel then F.notePanel.edit:ClearFocus()end
            F.tab=key;F.page=1;F.scroll:SetVerticalScroll(0);F.Render()
        end)
        b:SetHeight(30);F.tabButtons[key]=b;y=y+34
    end
    F.switchCharacter=button(F.sidebar,'Choose character',12,0,140,F.PickCharacter)
    F.sideContext=label(F.sidebar,'',12,0,140,'GameFontNormal')
    F.sideRealm=label(F.sidebar,'',12,0,140,'GameFontDisableSmall')
    F.sideVersion=label(F.sidebar,'',12,0,140,'GameFontDisableSmall')
    F.pageTitle=label(f,'Character',194,-19,400,'GameFontNormalLarge')
    F.pageContext=label(f,'',194,-45,400,'GameFontDisableSmall')
    local currentButton=button(f,'Current character',0,0,132,function()F.selected=F.current;F.scroll:SetVerticalScroll(0);F.Render()end)
    currentButton:ClearAllPoints();currentButton:SetPoint('TOPRIGHT',-132,-24)
    local refreshButton=button(f,'Refresh',0,0,76,function()F.Snapshot(true);F.DiscoverProfession();F.Render()end)
    refreshButton:ClearAllPoints();refreshButton:SetPoint('TOPRIGHT',-48,-24)
    local close=button(f,'X',0,0,26,function()f:Hide()end);close:ClearAllPoints();close:SetPoint('TOPRIGHT',-12,-24);F.closeButton=close
    for _,control in ipairs({currentButton,refreshButton,close})do control:SetFrameLevel(drag:GetFrameLevel()+5);control:EnableMouse(true);control:RegisterForClicks('LeftButtonUp')end
    F.scroll=CreateFrame('ScrollFrame',nil,f,'UIPanelScrollFrameTemplate')
    F.content=CreateFrame('Frame',nil,F.scroll);F.content:SetPoint('TOPLEFT',F.scroll,'TOPLEFT',0,0);F.scroll:SetScrollChild(F.content)
    local grip=CreateFrame('Button',nil,f);grip:SetSize(18,18);grip:SetPoint('BOTTOMRIGHT',-1,1);grip:SetNormalTexture('Interface/ChatFrame/UI-ChatIM-SizeGrabber-Up');F.resizeGrip=grip
    grip:SetScript('OnMouseDown',function(_,mouse)
        if mouse~='LeftButton' then return end
        local x,y=GetCursorPosition();local scale=f:GetEffectiveScale()
        F.resizing={x=x/scale,y=y/scale,w=f:GetWidth(),h=f:GetHeight()}
        local left,top=f:GetLeft(),f:GetTop()
        if left and top then f:ClearAllPoints();f:SetPoint('TOPLEFT',UIParent,'BOTTOMLEFT',left,top)end
        grip:SetScript('OnUpdate',function()
            local mx,my=GetCursorPosition();local r=F.resizing
            f:SetSize(math.max(940,math.min(UIParent:GetWidth()-20,r.w+mx/scale-r.x)),math.max(560,math.min(UIParent:GetHeight()-20,r.h+r.y-my/scale)))
        end)
    end)
    grip:SetScript('OnMouseUp',function()
        grip:SetScript('OnUpdate',nil);F.resizing=nil;F.db.settings.size={f:GetWidth(),f:GetHeight()}
        local a,_,b,x,y=f:GetPoint();F.db.settings.position={a,b,x,y};F.Render()
    end)
    f:SetScript('OnSizeChanged',function()if F.content and not F.rendering and not F.resizing then F.Render()end end)
    F.Layout()
end
function F.Show(tab)
    if not F.db then F.Init() end
    F.Snapshot(true);F.CreateWindow();F.selected=F.current;F.tab=tab or 'sheet';F.page=1;F.frame:Show();F.Render()
end
function F.Sheet(c)
    local w=F.width;local hero=card(0,0,w,108)
    if not hero.crest then hero.crest=hero:CreateTexture(nil,'ARTWORK')end
    hero.crest:ClearAllPoints();hero.crest:SetPoint('TOPLEFT',14,-16);hero.crest:SetSize(58,58);hero.crest:SetTexture(c.specIcon or 'Interface/Icons/INV_Misc_Book_09');hero.crest:Show()
    label(hero,M.Plain(c.name or 'Your character'),86,-14,w-248,'GameFontNormalHuge'):SetWordWrap(false)
    local title=(c.title or ''):gsub('%%s',c.name or '')
    label(hero,M.Plain(title~='' and title or ((c.race or 'Unknown race')..' '..(c.className or ''))),86,-43,w-248,'GameFontHighlight'):SetWordWrap(false)
    local identity=(c.race or 'Unknown race')..' | '..M.Spec(c)..' '..(c.className or '')..' | '..(c.faction or '?')..' | '..(c.guild or 'No guild')
    label(hero,M.Plain(identity),86,-66,w-106,'GameFontHighlightSmall'):SetWordWrap(false)
    tooltip(hero,M.Plain(c.name or 'Your character'),{M.Plain(title),M.Plain(identity),M.Plain(c.realm or 'Unknown realm')})
    label(hero,F.selected==F.current and 'THIS CHARACTER' or 'RECORDED CHARACTER',w-156,-18,142,'GameFontDisableSmall')
    button(hero,'Assign tags',w-138,-43,124,F.TagPicker)
    label(hero,M.Plain(M.TagText(c)~='' and ('Tags: '..M.TagText(c)) or 'No tags assigned'),14,-88,w-28,'GameFontDisableSmall'):SetWordWrap(false)
    local gap=8;local col=(w-3*gap)/4
    stat(0,116,col,'Level',M.Level(c));stat(col+gap,116,col,'Equipped item level',c.ilvl and string.format('%.1f',c.ilvl))
    stat(2*(col+gap),116,col,'Rested XP',M.Rested(c));stat(3*(col+gap),116,col,'Last spec role',c.role or 'Unknown')
    local y=section('Attributes',171)
    local attributes=card(0,y,w,128);local cell=(w-24)/4
    local fields={{'Strength',c.stats and c.stats.strength},{'Agility',c.stats and c.stats.agility},{'Stamina',c.stats and c.stats.stamina},{'Intellect',c.stats and c.stats.intellect},{'Health',c.health},{'Armor',c.stats and c.stats.armor},{'Crit',c.stats and c.stats.crit and string.format('%.1f%%',c.stats.crit)},{'Haste',c.stats and c.stats.haste and string.format('%.1f%%',c.stats.haste)},{'Mastery',c.stats and c.stats.mastery and string.format('%.1f%%',c.stats.mastery)},{'Speed rating',c.stats and c.stats.speedRating},{'Movement',c.stats and c.stats.movement and string.format('%.1f%%',c.stats.movement)},{'Speed bonus',c.stats and c.stats.speedBonus and string.format('%.1f%%',c.stats.speedBonus)}}
    for i,v in ipairs(fields)do
        local x=12+((i-1)%4)*cell;local top=8+math.floor((i-1)/4)*40
        label(attributes,v[1]:upper(),x,-top,cell-12,'GameFontDisableSmall')
        label(attributes,M.Plain(value(v[2])),x,-top-16,cell-12,'GameFontHighlight'):SetWordWrap(false)
    end
    y=y+140;y=section('Travel & whereabouts',y)
    local travel=card(0,y,w,72)
    label(travel,'HEARTHSTONE',12,-8,w*.45,'GameFontDisableSmall')
    label(travel,M.Plain(value(c.bind)),12,-25,w*.45,'GameFontHighlight'):SetWordWrap(false)
    label(travel,F.selected==F.current and 'CURRENT LOCATION' or 'LAST RECORDED LOCATION',w*.5,-8,w*.5-12,'GameFontDisableSmall')
    label(travel,M.Plain(value(c.subzone and c.subzone~='' and c.subzone or c.zone)),w*.5,-25,w*.5-12,'GameFontHighlight'):SetWordWrap(false)
    label(travel,M.Plain((c.zone or 'Unknown zone')..' | '..(c.realmRegion or 'Unknown region')..' | '..(c.loggedOut and 'Logged out: ' or 'Last seen: ')..stamp(c.lastSeen)),12,-52,w-24,'GameFontDisableSmall'):SetWordWrap(false)
    y=y+84
    local resume=card(0,y,w,94)
    label(resume,'WHERE I LEFT OFF',12,-10,w-160,'GameFontNormal')
    button(resume,'Edit next step',w-138,-7,124,function()F.noteSection='resume';F.tab='notes';F.scroll:SetVerticalScroll(0);F.Render()end)
    local nextStep=c.notes.resume or ''
    label(resume,M.Plain(nextStep~='' and nextStep or 'Leave one small next step for your next login.'),12,-36,w-24):SetHeight(32)
    label(resume,c.resumeUpdatedAt and ('Updated '..stamp(c.resumeUpdatedAt)) or 'Saved with this character; ready whenever you are.',12,-75,w-24,'GameFontDisableSmall')
    tooltip(resume,'Where I left off',{M.Plain(nextStep~='' and nextStep or 'No next step recorded.'),'Edit next step opens this character\'s notebook.'})
    y=y+108;y=section('Collection milestones',y)
    local collected=c.collections or {};local cw=(w-16)/3
    stat(0,y,cw,'Mounts (account)',collected.mounts);stat(cw+8,y,cw,'Pets (account)',collected.pets);stat(2*(cw+8),y,cw,'Achievement points',collected.achievementPoints)
    y=y+55;y=section('Purpose & plans',y)
    local plans=card(0,y,w,106);local note=c.notes.general or ''
    label(plans,M.Plain(note~='' and note or 'Capture what this character is for: a project, an adventure, a backstory.'),12,-10,w-24):SetHeight(46)
    button(plans,'Open Notebook',12,-70,140,function()F.noteSection='general';F.tab='notes';F.scroll:SetVerticalScroll(0);F.Render()end)
    button(plans,'Find another character',160,-70,172,function()F.tab='roster';F.scroll:SetVerticalScroll(0);F.Render()end)
    if C_AddOns and S(C_AddOns.IsAddOnLoaded,'DuckMooPlanner')then
        button(plans,'Concentration Planner',340,-70,176,function()if SlashCmdList.DUCKMOOPLANNER then SlashCmdList.DUCKMOOPLANNER('')end end)
    end
    F.content:SetHeight(y+118)
end
function F.Section(title,y,key)
    local id=(F.selected or '')..':'..key
    local collapsed=F.db.settings.sections[id]
    button(F.content,(collapsed and '[+] ' or '[-] ')..title,0,-y,F.width,function()
        F.db.settings.sections[id]=not F.db.settings.sections[id];F.Render()
    end)
    return y+28,not collapsed
end
function F.Skills(c)
    local y=0
    text('Open each profession to record learned expansion skills and specialization investment.',4,y,F.width-8,'GameFontHighlightSmall');y=y+28
    local list=sorted(c.professions)
    table.sort(list,function(a,b)
        local sa,sb=M.IsSecondary(a.value,a.id),M.IsSecondary(b.value,b.id)
        if sa~=sb then return not sa end
        return a.value.name<b.value.name
    end)
    local secondary=false
    for _,v in ipairs(list)do
        if v.id~=794 then
            local p=v.value
            if M.IsSecondary(p,v.id) and not secondary then y=section('Secondary trade skills',y+4);secondary=true end
            local open;y,open=F.Section(p.name..' | '..(p.rank or '?')..' / '..(p.max or '?'),y,'profession'..v.id)
            if open then
                local children=sorted(p.expansions)
                if #children==0 then text('Open this profession on this character to scan expansion skills.',8,y,F.width-16,'GameFontDisableSmall');y=y+24 end
                for _,e in ipairs(children)do
                    local r=e.value;local row=card(0,y,F.width,40)
                    label(row,M.Plain(r.name),8,-4,F.width-160)
                    label(row,(r.rank or '?')..' / '..(r.max or '?'),F.width-140,-4,130)
                    label(row,r.recipes and ('Known recipes in last filtered scan: '..r.recipes) or ('Updated '..stamp(r.seenAt)),8,-23,F.width-16,'GameFontDisableSmall');y=y+44
                    for _,node in ipairs(r.knowledge or {})do text(node.name..' | '..node.rank..(node.max and (' / '..node.max) or ''),12,y,F.width-24,'GameFontHighlightSmall');y=y+20 end
                end
            end
        end
    end
    if #list==0 then text('No professions recorded yet. Log into this character to collect them.',8,y,F.width-16);y=y+28 end
    local open;y,open=F.Section('Specialization',y+4,'specialization')
    if open then text(M.Spec(c),8,y,F.width-16);y=y+26 end
    y,open=F.Section('Earned titles ('..#(c.titles or {})..')',y+4,'titles')
    if open then for _,title in ipairs(c.titles or {})do text(title:gsub('%%s',c.name or ''),8,y,F.width-16);y=y+21 end end
    F.content:SetHeight(y+8)
end
function F.Reps(c)
    local y=section('Reputations you have encountered',0)
    text('Shared reputations are marked Warband. Use the Warband filter to compare characters by a reputation.',4,y,F.width-8,'GameFontDisableSmall'):SetHeight(30);y=y+40
    for _,v in ipairs(sorted(c.reputations)) do
        local r=v.value;local row=card(0,y,F.width,48)
        label(row,M.Plain(r.name),10,-6,F.width*.45)
        label(row,M.Plain(M.ReputationText(r)),F.width*.47,-6,F.width*.51,'GameFontNormal')
        label(row,r.accountWide and 'Warband reputation' or 'Character reputation',10,-27,200,'GameFontDisableSmall')
        local fraction=(r.max or 0)>(r.min or 0) and math.max(0,math.min(1,((r.value or 0)-(r.min or 0))/((r.max or 0)-(r.min or 0)))) or 1
        if not row.bar then row.bar=row:CreateTexture(nil,'ARTWORK');row.bar:SetTexture('Interface/Buttons/WHITE8X8');row.bar:SetPoint('BOTTOMLEFT',1,1);row.bar:SetHeight(2);row.bar:SetVertexColor(.6,.4,.9,1) end
        row.bar:Show();row.bar:SetWidth(math.max(1,(F.width-2)*fraction));y=y+53
    end
    if not next(c.reputations or {}) then text('No reputations recorded. Log into this character to refresh the folio.',8,y,F.width-16);y=y+28 end
    F.content:SetHeight(y+20)
end
function F.TagPicker()
    local p=F.tagPicker
    if not p then
        local dynamic=F.dynamic;F.dynamic=false
        p=panel(UIParent,'DuckMooFolioTags');F.tagPicker=p;p:SetSize(620,410);p:SetPoint('CENTER');p:SetFrameStrata('DIALOG');table.insert(UISpecialFrames,'DuckMooFolioTags')
        p.title=label(p,'Assign character tags',12,-12,590,'GameFontNormalLarge')
        p.rows={};for i=1,27 do
            local index=i
            p.rows[i]=button(p,'',12+((i-1)%3)*200,-44-math.floor((i-1)/3)*29,194,function()
                local tag=p.options[(p.page-1)*27+index]
                if tag then local key=tag:lower();p.draft[key]=not p.draft[key] and tag or nil;p.draw()end
            end)
        end
        p.input=CreateFrame('EditBox',nil,p,'InputBoxTemplate');p.input:SetPoint('TOPLEFT',20,-309);p.input:SetSize(435,25);p.input:SetAutoFocus(false);p.input:EnableMouse(true);p.input:SetMaxLetters(60)
        p.input:SetScript('OnEscapePressed',function(self)self:ClearFocus()end)
        p.add=function()
            local tags=M.Tags(p.input:GetText())
            for key,tag in pairs(tags)do F.db.settings.customTags[key]=tag;p.draft[key]=tag end
            p.input:SetText('');p.rebuild();p.draw()
        end
        p.input:SetScript('OnEnterPressed',p.add)
        button(p,'Add custom tag',467,-309,141,p.add)
        button(p,'<',12,-347,36,function()p.page=math.max(1,p.page-1);p.draw()end)
        button(p,'>',54,-347,36,function()p.page=p.page+1;p.draw()end)
        p.status=label(p,'',104,-351,240,'GameFontHighlightSmall')
        button(p,'Cancel',401,-347,90,function()p.input:ClearFocus();p:Hide()end)
        button(p,'Save tags',498,-347,110,function()
            if p.input:GetText():match('%S')then p.add()end
            local c=F.db.characters[p.guid];if c then c.tags=F.Clean(p.draft)end
            p.input:ClearFocus();p:Hide();F.Render()
        end)
        label(p,'Check any that fit. Add your own. Save tags to attach them to this character.',12,-383,596,'GameFontHighlightSmall')
        p.rebuild=function()
            local all={};for _,tag in ipairs(M.CommonTags)do all[tag:lower()]=tag end
            for key,tag in pairs(F.db.settings.customTags)do all[key]=tag end
            for key,tag in pairs(p.draft)do all[key]=tag end
            p.options={};for _,tag in pairs(all)do p.options[#p.options+1]=tag end;table.sort(p.options)
        end
        p.draw=function()
            local pages=math.max(1,math.ceil(#p.options/27));p.page=math.min(p.page,pages)
            for i,b in ipairs(p.rows)do local tag=p.options[(p.page-1)*27+i];b:SetShown(tag~=nil)
                if tag then b._active=p.draft[tag:lower()]~=nil;b:SetText((b._active and '[x] ' or '[ ] ')..tag)end
            end
            p.status:SetText('Page '..p.page..' / '..pages);F.ApplyTheme()
        end
        F.dynamic=dynamic
    end
    F.db.settings.customTags=F.db.settings.customTags or {}
    p.guid=F.selected;p.draft=F.Clean(F.db.characters[p.guid].tags or {});p.page=1;p.title:SetText('Assign tags: '..F.db.characters[p.guid].name);p.input:SetText('');p.rebuild();p:Show();p.draw()
end
function F.Notes(c)
    local n=F.notePanel
    if not n then
        local dynamic=F.dynamic;F.dynamic=false
        n=CreateFrame('Frame',nil,F.content);F.notePanel=n;n:SetPoint('TOPLEFT',0,0)
        n.rail=panel(n);n.rail:SetPoint('TOPLEFT',0,0);n.rail:SetWidth(164)
        label(n.rail,'NOTEBOOK',12,-12,140,'GameFontNormal')
        n.categories={}
        for i,v in ipairs({{'resume','Where I left off'},{'general','Purpose & plans'},{'adventuring','Adventuring'},{'professions','Professions'},{'backstory','Backstory'}})do
            local key=v[1]
            n.categories[key]=button(n.rail,v[2],8,-42-(i-1)*36,148,function()n.edit:ClearFocus();F.noteSection=key;F.Render()end)
            n.categories[key]:SetHeight(30)
        end
        button(n.rail,'Assign tags',8,-236,148,F.TagPicker)
        n.tagsLabel=label(n.rail,'',12,-277,140,'GameFontDisableSmall');n.tagsLabel:SetWordWrap(true);n.tagsLabel:SetHeight(74)
        n.paper=panel(n);n.paper:SetPoint('TOPLEFT',176,0)
        n.title=label(n.paper,'',14,-14,400,'GameFontNormalLarge')
        n.subtitle=label(n.paper,'',14,-42,400,'GameFontDisableSmall')
        n.scroll=CreateFrame('ScrollFrame',nil,n.paper,'UIPanelScrollFrameTemplate');n.scroll:SetPoint('TOPLEFT',18,-76);n.scroll:EnableMouse(true)
        n.edit=CreateFrame('EditBox',nil,n.scroll);n.edit:SetPoint('TOPLEFT',n.scroll,'TOPLEFT',0,0);n.edit:SetMultiLine(true);n.edit:SetAutoFocus(false);n.edit:EnableMouse(true);n.edit:SetFontObject('GameFontHighlight');n.edit:SetMaxLetters(30000)
        n.scroll:SetScrollChild(n.edit);n.scroll:SetScript('OnMouseDown',function()n.edit:SetFocus()end)
        n.measure=n:CreateFontString(nil,'OVERLAY','GameFontHighlight');n.measure:Hide();n.measure:SetWordWrap(true)
        n.save=function()
            if n.loading or not n.guid then return end
            local character=F.db.characters[n.guid]
            if character then
                if n.section=='resume' then F.SaveResume(n.guid,n.edit:GetText())else character.notes[n.section]=n.edit:GetText()end
                n.saved:SetText('Saved for '..character.name..'.')
            end
        end
        n.edit:SetScript('OnTextChanged',function(self)
            n.measure:SetText(M.Plain(self:GetText()));self:SetHeight(math.max(n.editHeight or 240,(n.measure:GetStringHeight() or 240)+24));n.save()
        end)
        n.edit:SetScript('OnEscapePressed',function(self)n.save();self:ClearFocus()end)
        n.saveButton=button(n.paper,'Save note',14,0,112,function()n.save();n.edit:ClearFocus()end)
        n.saved=label(n.paper,'Notes save as you type.',140,0,300,'GameFontDisableSmall')
        F.dynamic=dynamic
    end
    local height=math.max(390,F.viewportHeight-8);local paperWidth=F.width-176
    n:Show();n:SetSize(F.width,height);n.rail:SetHeight(height);n.paper:SetSize(paperWidth,height)
    n.scroll:SetSize(paperWidth-48,height-130);n.editHeight=height-130
    n.edit:SetWidth(paperWidth-54);n.measure:SetWidth(paperWidth-54);n.edit:SetHeight(math.max(n.editHeight,(n.measure:GetStringHeight()or 0)+24))
    n.title:SetWidth(paperWidth-28);n.subtitle:SetWidth(paperWidth-28)
    n.saveButton:ClearAllPoints();n.saveButton:SetPoint('TOPLEFT',14,-height+38)
    n.saved:ClearAllPoints();n.saved:SetPoint('TOPLEFT',140,-height+44);n.saved:SetWidth(paperWidth-156)
    n.tagsLabel:SetText(M.Plain(M.TagText(c)~='' and ('Tags: '..M.TagText(c)) or 'No tags assigned'))
    local section=F.noteSection or 'general'
    if n.guid~=F.selected or n.section~=section then
        n.loading=true;n.edit:ClearFocus();n.guid=F.selected;n.section=section;n.edit:SetText(c.notes[section] or '');n.saved:SetText('Notes save as you type.');n.loading=false
    end
    local names={resume='Where I left off',general='Purpose & plans',adventuring='Adventuring',professions='Professions',backstory='Backstory'}
    n.title:SetText(names[n.section] or 'Notebook');n.subtitle:SetText(M.Plain((c.name or '?')..' - '..(c.realm or '?')..' | '..(F.selected==F.current and 'This character' or 'Offline notes are editable')))
    for key,b in pairs(n.categories)do b._active=key==n.section end
    F.content:SetHeight(height)
end
function F.RosterViewEditor()
    local p=F.viewEditor
    if not p then
        local dynamic=F.dynamic;F.dynamic=false
        p=panel(UIParent,'DuckMooFolioViewEditor');F.viewEditor=p
        p:SetSize(410,150);p:SetPoint('CENTER');p:SetFrameStrata('DIALOG');p:SetClampedToScreen(true)
        table.insert(UISpecialFrames,'DuckMooFolioViewEditor')
        label(p,'Save this roster view',14,-12,370,'GameFontNormalLarge')
        label(p,'Name these filters, search and grouping. Reusing a name updates it.',14,-40,370,'GameFontHighlightSmall'):SetHeight(30)
        p.edit=CreateFrame('EditBox',nil,p,'InputBoxTemplate');p.edit:SetPoint('TOPLEFT',22,-78);p.edit:SetSize(360,24);p.edit:SetAutoFocus(false);p.edit:SetMaxLetters(60)
        p.save=button(p,'Save',14,-115,100,function()if F.SaveRosterView(p.edit:GetText())then p:Hide();F.Render()end end)
        button(p,'Cancel',296,-115,100,function()p:Hide()end)
        p.edit:SetScript('OnEscapePressed',function()p:Hide()end)
        F.dynamic=dynamic
    end
    local t=theme();p.edit:SetTextColor(unpack(t.text));p.edit:SetText('');p:Show();p.edit:SetFocus();F.ApplyTheme()
end
function F.RosterViewPicker(remove)
    local options={}
    for name in pairs(F.db.settings.rosterViews)do options[#options+1]={id=name,name=name}end
    table.sort(options,function(a,b)return a.name<b.name end)
    if #options==0 then F.Print('No saved views yet. Set your filters and choose Save view.');return end
    F.Choose(remove and 'Remove a saved view' or 'Choose a saved view',options,function(name)
        if remove then F.db.settings.rosterViews[name]=nil else F.ApplyRosterView(name) end
        F.Render()
    end)
end
function F.Choose(title,options,onSelect)
    local choice=F.choice
    if not choice then
        local dynamic=F.dynamic;F.dynamic=false
        choice=panel(UIParent,'DuckMooFolioChooser');F.choice=choice;choice:SetSize(430,450);choice:SetPoint('CENTER');choice:SetFrameStrata('DIALOG');table.insert(UISpecialFrames,'DuckMooFolioChooser')
        choice.title=label(choice,'',14,-14,365,'GameFontNormalLarge')
        button(choice,'X',390,-10,25,function()choice:Hide()end)
        choice.search=CreateFrame('EditBox',nil,choice,'InputBoxTemplate');choice.search:SetPoint('TOPLEFT',21,-48);choice.search:SetSize(380,25);choice.search:SetAutoFocus(false)
        choice.rows={};for i=1,12 do choice.rows[i]=button(choice,'',15,-80-(i-1)*26,395,function()end) end
        button(choice,'Previous',15,-408,90,function()choice.page=math.max(1,choice.page-1);choice.draw()end)
        button(choice,'Next',320,-408,90,function()choice.page=choice.page+1;choice.draw()end)
        choice.counter=label(choice,'',120,-414,190,'GameFontDisableSmall')
        choice.draw=function()
            local matches={};local query=choice.search:GetText():lower()
            for _,o in ipairs(choice.options) do if o.name:lower():find(query,1,true) then matches[#matches+1]=o end end
            local pages=math.max(1,math.ceil(#matches/12));choice.page=math.min(choice.page,pages)
            for i,b in ipairs(choice.rows) do
                local o=matches[(choice.page-1)*12+i];b:SetShown(o~=nil)
                if o then b:SetText(M.Plain(o.name));b:SetScript('OnClick',function()choice:Hide();choice.callback(o.id,o.name)end) end
            end
            choice.counter:SetText('Page '..choice.page..' / '..pages)
        end
        choice.search:SetScript('OnTextChanged',function()choice.page=1;if choice.options then choice.draw()end end)
        F.dynamic=dynamic
    end
    choice.options=options;choice.callback=onSelect;choice.page=1;choice.title:SetText(title);choice.search:SetText('');choice:Show();choice.draw()
end
function F.FilterControl(kind,title,options,x,y,w)
    local filter=F.filters;local caption=title
    if filter[kind] then for _,o in ipairs(options) do if o.id==filter[kind] then caption=o.name;break end end end
    local b=button(F.content,caption,x,-y,w,function()
        local all={{name='All '..title,id=false}}
        for _,o in ipairs(options) do all[#all+1]=o end
        F.Choose(title,all,function(id)
            filter[kind]=id or nil;if kind=='profession' then filter.expansion=nil end
            F.page=1;F.Render()
        end)
    end)
    tooltip(b,title,{M.Plain(caption),'Click to choose or clear this filter. Filters combine.'})
end

function F.Roster()
    local f=F.filters;local w=F.width;local col=(w-18)/4
    if not F.rosterSearch then
        F.rosterSearch=CreateFrame('EditBox',nil,F.content,'InputBoxTemplate');F.rosterSearch:SetHeight(26);F.rosterSearch:SetAutoFocus(false);F.rosterSearch:SetMaxLetters(100)
        F.rosterSearch:SetScript('OnTextChanged',function(self,user)if user then F.filters.search=self:GetText();F.page=1;F.Render()end end)
        F.rosterSearch:SetScript('OnEscapePressed',function(self)self:ClearFocus()end)
        F.rosterSearch.hint=label(F.rosterSearch,'Search characters, tags or notes',2,-7,300,'GameFontDisableSmall')
        tooltip(F.rosterSearch,'Search your characters',{'Search names, realms, specializations, tags and notebook text.'})
    end
    F.rosterSearch:Show();F.rosterSearch:ClearAllPoints();F.rosterSearch:SetPoint('TOPLEFT',8,-2);F.rosterSearch:SetWidth(w-314)
    if not F.rosterSearch:HasFocus()then F.rosterSearch:SetText(f.search or '')end
    F.rosterSearch.hint:SetShown(F.rosterSearch:GetText()=='')
    local active=0;for key,v in pairs(f)do if key~='search' and key~='sort' and v then active=active+1 end end
    button(F.content,'Filters'..(active>0 and (' ('..active..')') or ''),w-300,0,90,function()F.rosterFiltersOpen=not F.rosterFiltersOpen;F.Render()end)
    button(F.content,'Saved views',w-204,0,112,function()F.RosterViewPicker(false)end)
    button(F.content,'Save view',w-86,0,86,F.RosterViewEditor)
    F.FilterControl('sort','Sort',{{id='level',name='Level & XP'},{id='ilvl',name='Item level'},{id='rested',name='Rested XP'},{id='name',name='Name'}},0,36,174)
    button(F.content,F.flatRoster and 'Group by realm' or 'Flat ranking',182,-36,154,function()F.flatRoster=not F.flatRoster;F.page=1;F.Render()end)
    button(F.content,'Clear filters',344,-36,108,function()F.filters={};F.page=1;F.rosterSearch:ClearFocus();F.rosterSearch:SetText('');F.Render()end)
    button(F.content,'Remove saved view',460,-36,152,function()F.RosterViewPicker(true)end)
    local base=78
    if F.rosterFiltersOpen then
    local classes={};for i=1,20 do local name,token=S(GetClassInfo,i);if name and token then classes[#classes+1]={id=token,name=name}end end
    if #classes==0 then classes=M.Options(F.db,'class') end
    F.FilterControl('class','Class',classes,0,72,col)
    F.FilterControl('role','Role',{{id='TANK',name='Tank'},{id='HEALER',name='Healer'}},col+6,72,col)
    F.FilterControl('faction','Faction',{{id='Alliance',name='Alliance'},{id='Horde',name='Horde'}},2*(col+6),72,col)
    F.FilterControl('region','Region',{{id='NA-US',name='NA-US'},{id='NA-OCE',name='NA-OCE'},{id='NA-LATAM',name='NA-LATAM'},{id='NA-BR',name='NA-BR'},{id='EU',name='EU'},{id='KR',name='KR'},{id='TW',name='TW'}},3*(col+6),72,col)
    F.FilterControl('profession','Profession',M.Options(F.db,'profession'),0,106,col)
    F.FilterControl('expansion','Expansion skill',M.Options(F.db,'expansion',f.profession),col+6,106,col)
    F.FilterControl('reputation','Reputation',M.Options(F.db,'reputation'),2*(col+6),106,col)
    F.FilterControl('tag','Tag',M.Options(F.db,'tag'),3*(col+6),106,col)
    F.FilterControl('realm','Realm',M.Options(F.db,'realm'),0,140,col)
    text('Filters combine. Role searches include capable classes.',col+12,146,w-col-18,'GameFontDisableSmall')

        base=182
    end
    local entries=M.Roster(F.db,f);F.filteredRoster=entries
    local grouped=not F.flatRoster and not f.role and not f.reputation
    local rows=grouped and M.Grouped(entries,F.db.settings.collapsed)or entries
    local pageSize=math.max(4,math.min(20,math.floor((F.viewportHeight-base-96)/48)))
    F.rosterPageSize=pageSize
    -- Keep realm headings with their characters, repeating the heading when a
    -- large realm continues on the next page. Collapsed headings remain usable.
    local pageRows={{}};local chunk=pageRows[1];local realmHeader
    for index,e in ipairs(rows)do
        local hasChildren=e.header and rows[index+1] and not rows[index+1].header
        if #chunk>=pageSize or (hasChildren and #chunk>=pageSize-1)then
            chunk={};pageRows[#pageRows+1]=chunk
            if not e.header and realmHeader then chunk[#chunk+1]=realmHeader end
        end
        chunk[#chunk+1]=e
        if e.header then realmHeader=e end
    end
    local pages=#pageRows;F.page=math.max(1,math.min(F.page or 1,pages))
    F.rosterVisibleRows=pageRows[F.page];F.rosterPages=pageRows
    text(#entries..' characters | '..(grouped and 'Grouped by realm' or 'Flat ranking')..' | Page '..F.page..' / '..pages,4,base+4,w-210,'GameFontDisableSmall')
    button(F.content,'<',w-154,-base,34,function()F.page=math.max(1,F.page-1);F.Render()end)
    button(F.content,'>',w-112,-base,34,function()F.page=math.min(pages,F.page+1);F.Render()end)
    button(F.content,'All realms',w-70,-base,70,function()F.db.settings.collapsed={};F.filters.realm=nil;F.page=1;F.Render()end)
    local header=base+36
    text('CHARACTER / REALM',8,header,w*.40,'GameFontDisableSmall');text('LEVEL',w*.41,header,60,'GameFontDisableSmall')
    text('iLVL',w*.50,header,65,'GameFontDisableSmall');text('RESTED',w*.59,header,70,'GameFontDisableSmall')
    text(f.reputation and 'REPUTATION' or 'LAST SPEC / FACTION',w*.70,header,w*.29,'GameFontDisableSmall')
    local y=header+24
    for _,e in ipairs(F.rosterVisibleRows)do
        if e.header then
            button(F.content,(F.db.settings.collapsed[e.header]and '[+] 'or '[-] ')..e.header..' ('..e.count..')',0,-y,w,function()F.db.settings.collapsed[e.header]=not F.db.settings.collapsed[e.header];F.Render()end);y=y+30
        else
            local c=e.c;local row=button(F.content,'',0,-y,w,function()F.selected=e.guid;F.tab='sheet';F.scroll:SetVerticalScroll(0);F.Render()end);row:SetHeight(44)
            local name=label(row,M.Plain(c.name or '?'),10,-6,w*.39,'GameFontNormal');name:SetWordWrap(false)
            local color=RAID_CLASS_COLORS and RAID_CLASS_COLORS[c.class]
            if color and theme().text[1]>.5 then name._fixedColor={color.r,color.g,color.b};name:SetTextColor(color.r,color.g,color.b)end
            label(row,M.Plain((c.realm or '?')..' | '..(c.realmRegion or '?')),10,-26,w*.39,'GameFontDisableSmall'):SetWordWrap(false)
            label(row,M.Level(c),w*.41,-8,65);label(row,c.ilvl and string.format('%.1f',c.ilvl)or '?',w*.50,-8,65)
            label(row,M.Rested(c),w*.59,-8,65)
            label(row,M.Plain(f.reputation and M.ReputationText(c.reputations[f.reputation])or M.Spec(c)),w*.70,-6,w*.29,'GameFontHighlightSmall'):SetWordWrap(false)
            label(row,M.Plain((c.faction or '?')..(f.reputation and c.reputations[f.reputation].accountWide and ' | Warband rep'or '')),w*.70,-26,w*.29,'GameFontDisableSmall'):SetWordWrap(false)
            tooltip(row,(c.name or '?')..'-'..(c.realm or '?'),{M.Plain(M.Spec(c)),M.Plain(M.TagText(c)),'Last updated: '..stamp(c.lastSeen),'Click to open this character folio.'});y=y+48
        end
    end
    if #entries==0 then text('No recorded character matches. Clear filters or record more characters.',8,y,w-16);y=y+30 end
    text('Role searches include capable classes and rank the last recorded role first. Offline data keeps its observation time.',4,y+8,w-8,'GameFontDisableSmall'):SetHeight(30)
    F.content:SetHeight(y+46)
end
function F.Coverage()
    local w=F.width;F.coverageFilters=F.coverageFilters or {};local filter=F.coverageFilters
    button(F.content,'Warband census',0,0,140,function()F.censusMode=nil;F.Render()end)
    text('PROFESSION BLINDSPOTS',152,5,w-152,'GameFontNormalLarge')
    local rows,summary=M.ProfessionCoverage(F.db)
    text(summary.covered..' covered | '..summary.gap..' with no owner recorded | '..summary.needs_scan..' need scanning',4,35,w-8,'GameFontHighlightSmall')
    text('Coverage means a recorded learned expansion skill, not every recipe collected. Log into your alts and open professions to resolve scan gaps.',4,57,w-8,'GameFontHighlightSmall'):SetHeight(30)
    text(summary.unknownCharacters..' characters have no profession snapshot. No owner recorded is a lead to investigate, not proof of an account-wide gap.',4,91,w-8,'GameFontDisableSmall'):SetHeight(30)
    local col=(w-12)/3
    button(F.content,filter.profession and ('Profession: '..filter.profession) or 'All professions',0,-126,col,function()
        local options={{id=false,name='All professions'}};for _,p in ipairs(M.CoverageProfessions)do options[#options+1]={id=p.id,name=p.name}end
        F.Choose('Profession coverage',options,function(id,name)filter.professionID=id or nil;filter.profession=id and name or nil;F.coveragePage=1;F.Render()end)
    end)
    button(F.content,filter.tier and M.CoverageExpansions[filter.tier] or 'All expansions',col+6,-126,col,function()
        local options={{id=false,name='All expansions'}};for tier,name in ipairs(M.CoverageExpansions)do options[#options+1]={id=tier,name=name}end
        F.Choose('Expansion coverage',options,function(id)filter.tier=id or nil;F.coveragePage=1;F.Render()end)
    end)
    button(F.content,filter.all and 'Show blindspots' or 'Show all coverage',2*(col+6),-126,col,function()filter.all=not filter.all;F.coveragePage=1;F.Render()end)
    local visible={}
    for _,r in ipairs(rows)do if (not filter.professionID or r.professionID==filter.professionID) and (not filter.tier or r.tier==filter.tier) and (filter.all or r.status~='covered')then visible[#visible+1]=r end end
    table.sort(visible,function(a,b)if a.tier~=b.tier then return a.tier>b.tier end;return a.profession<b.profession end)
    F.coverageRows=visible
    local pages=math.max(1,math.ceil(#visible/20));F.coveragePage=math.min(F.coveragePage or 1,pages)
    text(#visible..' expansion skills | Page '..F.coveragePage..' / '..pages,4,161,w-100,'GameFontDisableSmall')
    button(F.content,'<',w-82,-154,36,function()F.coveragePage=math.max(1,F.coveragePage-1);F.Render()end)
    button(F.content,'>',w-40,-154,36,function()F.coveragePage=math.min(pages,F.coveragePage+1);F.Render()end)
    local y=184
    for index=(F.coveragePage-1)*20+1,math.min(#visible,F.coveragePage*20)do
        local r=visible[index];local row=button(F.content,'',0,-y,w,function()
            F.filters={profession=r.profession};if #r.owners>0 then F.filters.expansion=r.expansionID end
            F.tab='roster';F.page=1;F.Render()
        end);row:SetHeight(43)
        label(row,M.Plain(r.name),8,-5,w*.61,'GameFontHighlightSmall')
        label(row,r.expansion,8,-25,w*.61,'GameFontDisableSmall')
        local status=r.status=='covered' and (#r.owners..' owner(s)') or r.status=='needs_scan' and (#r.pending..' owner(s) need scanning') or 'No owner recorded'
        label(row,status,w*.63,-5,w*.35,'GameFontNormal')
        local hint=r.owners[1] and (r.owners[1].c.name..' | '..r.owners[1].rank..' / '..(r.owners[1].max or '?')) or (#r.pending>0 and 'Click to find characters to scan' or 'No trained character in saved snapshots')
        label(row,M.Plain(hint),w*.63,-25,w*.35,'GameFontDisableSmall')
        local lines={status,'Click to find recorded owners or characters with this base profession.'}
        for i=1,math.min(8,#r.owners)do local owner=r.owners[i];lines[#lines+1]=(owner.c.name or '?')..'-'..(owner.c.realm or '?')..': '..owner.rank..' / '..(owner.max or '?')end
        tooltip(row,r.name,lines);y=y+47
    end
    if #visible==0 then text('No blindspots match these filters. Show all coverage to inspect your recorded owners.',8,y,w-16);y=y+28 end
    F.content:SetHeight(y+8)
end
function F.Census()
    if F.censusMode=='coverage' then F.Coverage();return end
    button(F.content,'Profession blindspots',0,0,180,function()F.censusMode='coverage';F.coveragePage=1;F.Render()end)
    local c=M.Census(F.db);local y=section('The Warband Census',34)
    text(c.total..' recorded adventurers. Census counts reflect characters you have logged into with this addon.',8,y,F.width-16);y=y+36
    local categories={{'Faction','faction'},{'Class','class'},{'Race','race'},{'Profession','profession'},{'Level band','band'},{'Realm','realm'},{'Your tags','tag'}}
    for _,v in ipairs(categories) do
        y=section(v[1],y)
        local list={};for name,count in pairs(c[v[2]]) do list[#list+1]={name=name,count=count}end
        table.sort(list,function(a,b)return a.name<b.name end)
        for i,r in ipairs(list) do
            local col=(F.width-16)/3
            stat(((i-1)%3)*(col+8),y+math.floor((i-1)/3)*47,col,r.name,r.count)
        end
        if #list==0 then text('None recorded yet.',8,y,F.width-16,'GameFontDisableSmall');y=y+26 else y=y+math.ceil(#list/3)*47 end
        y=y+10
    end
    y=section('Nearest to the next ding',y)
    local low={};for _,ch in pairs(F.db.characters) do if ch.level and ch.maxLevel and ch.level<ch.maxLevel and ch.xpMax and ch.xpMax>0 then low[#low+1]=ch end end
    table.sort(low,function(a,b)return (a.xp or 0)/a.xpMax>(b.xp or 0)/b.xpMax end)
    for i=1,math.min(5,#low) do local ch=low[i];text(ch.name..'-'..ch.realm..' | '..M.Level(ch),8,y,F.width-16);y=y+25 end
    F.content:SetHeight(y+20)
end
function F.Collection(c)
    local y=section('Collector field notes | All The Things',0)
    local app,message=F.ATTStatus()
    if message then text(message,8,y,F.width-16):SetHeight(65);y=y+75 end
    if F.attMessage then text(F.attMessage,8,y,F.width-16):SetHeight(40);y=y+48 end
    if app then
        button(F.content,'Open ATT',4,-y,110,F.OpenATT)
        if F.selected==F.current then button(F.content,F.attBusy and 'Reading...' or 'Refresh opportunities',122,-y,180,F.RefreshATT) end
        y=y+38
    end
    local snapshot=c.att
    if not snapshot then
        text('No ATT snapshot for this character yet. Log into them, enable ATT, open its main list, and click Refresh opportunities.',8,y,F.width-16):SetHeight(60);F.content:SetHeight(y+75);return
    end
    text('Recorded '..stamp(snapshot.seenAt)..' | '..M.Display(snapshot.mode),6,y,F.width-12,'GameFontDisableSmall'):SetHeight(32);y=y+40
    text('Counts follow the ATT profile used at capture, including its account/character and availability filters. These are opportunities, not drop chances or guaranteed obtainable items. Legacy instances stop at Dragonflight. The War Within, Midnight, and instances with an unknown expansion are excluded.',6,y,F.width-12,'GameFontHighlightSmall'):SetHeight(50);y=y+60
    local target=F.GetATDART(snapshot)
    local targetCard=card(0,y,F.width,target and 52 or 60)
    label(targetCard,'ATDART % Target',8,-6,F.width-16,'GameFontNormal')
    if target then
        label(targetCard,M.Plain(M.Display(target.name)),8,-28,F.width-112)
        label(targetCard,string.format('%.2f%%',100*target.progress/target.total),F.width-98,-26,90,'GameFontNormalLarge')
        tooltip(targetCard,'ATDART % Target',{M.Plain(M.Display(target.name)),target.progress..' / '..target.total..' collected in this ATT profile','Lowest completion across recorded legacy dungeons and raids. Ties are picked once per snapshot.'})
    else
        label(targetCard,snapshot.completion and 'No eligible legacy instances in this ATT snapshot.' or 'Refresh ATT opportunities on this character to record completion totals.',8,-28,F.width-16,'GameFontHighlightSmall')
    end
    y=y+(target and 58 or 66)
    for _,v in ipairs({{'Legacy dungeons','dungeons'},{'Legacy raids','raids'},{'Zones with unfinished quests','zones'}}) do
        y=section(v[1],y)
        local list={}
        for _,r in ipairs(snapshot[v[2]] or {})do if v[2]=='zones' or F.IsLegacyATT(r)then list[#list+1]=r end end
        local expansion=F.attExpansion
        if v[2]~='zones' and (expansion=='The War Within' or expansion=='Midnight')then expansion=nil end
        local opts={};local found={};for _,r in ipairs(list)do local name=F.ATTExpansionLabel(r,v[2]=='zones');found[name]=true end
        for name in pairs(found)do opts[#opts+1]={id=name,name=name}end;table.sort(opts,function(a,b)return a.name<b.name end)
        button(F.content,expansion or 'All expansions',4,-y,250,function()
            local all={{id=false,name='All expansions'}};for _,o in ipairs(opts)do all[#all+1]=o end
            F.Choose('Expansion',all,function(id)F.attExpansion=id or nil;F.Render()end)
        end);y=y+33
        local shown=0
        for _,r in ipairs(list) do
            local expansionName=F.ATTExpansionLabel(r,v[2]=='zones')
            if not expansion or expansionName==expansion then
                local row=card(0,y,F.width,43)
                label(row,M.Plain(M.Display(r.name)),8,-6,F.width-150)
                label(row,r.missing..(v[2]=='zones' and ' quests' or ' missing'),F.width-140,-6,130,'GameFontNormal')
                label(row,M.Plain(expansionName),8,-25,F.width-16,'GameFontDisableSmall');y=y+48;shown=shown+1
                if shown>=15 then break end
            end
        end
        if shown==0 then text('No matching opportunities in this ATT snapshot. Hidden or unprepared ATT groups may not appear.',8,y,F.width-16,'GameFontDisableSmall'):SetHeight(28);y=y+36 end
        y=y+10
    end
    F.content:SetHeight(y+20)
end
function F.Settings(c)
    local y=section('Folio settings',0)
    local function paragraph(s,font)
        local f=text(s,6,y,F.width-12,font or 'GameFontHighlight');f:SetFont(STANDARD_TEXT_FONT or 'Fonts/FRIZQT__.TTF',14)
        local h=f:GetStringHeight() or math.ceil(#s/math.max(1,(F.width-12)/7))*18
        f:SetHeight(h);y=y+h+8
    end
    paragraph('Realm: '..(c.realmRegion or 'Unknown')..'. Americas realms are automatically labeled NA-US, NA-OCE, NA-LATAM, or NA-BR.')
    button(F.content,'Theme: '..theme().name,4,-y,240,function()
        local options={};for id,t in pairs(F.Themes)do options[#options+1]={id=id,name=t.name}end;table.sort(options,function(a,b)return a.name<b.name end)
        F.Choose('Window theme',options,function(id)if id then F.db.settings.theme=id;F.Render()end end)
    end);y=y+34
    if not F.opacitySlider then
        local dynamic=F.dynamic;F.dynamic=false
        F.opacityValue=label(F.content,'',6,0,500)
        local slider=CreateFrame('Slider',nil,F.content,'OptionsSliderTemplate');F.opacitySlider=slider;slider:SetSize(270,18);slider:SetMinMaxValues(20,100);slider:SetValueStep(1);if slider.SetObeyStepOnDrag then slider:SetObeyStepOnDrag(true)end
        slider:SetScript('OnValueChanged',function(_,v)F.db.settings.backgroundAlpha=v/100;F.opacityValue:SetText('Background opacity: '..math.floor(v+.5)..'%');F.ApplyTheme()end)
        F.dynamic=dynamic
    end
    F.opacityValue:Show();F.opacityValue:ClearAllPoints();F.opacityValue:SetPoint('TOPLEFT',6,-y);y=y+25
    F.opacitySlider:Show();F.opacitySlider:ClearAllPoints();F.opacitySlider:SetPoint('TOPLEFT',12,-y);F.opacitySlider:SetValue((F.db.settings.backgroundAlpha or .92)*100);y=y+34
    button(F.content,F.db.settings.hideMinimap and 'Show minimap button' or 'Hide minimap button',4,-y,210,function()F.db.settings.hideMinimap=not F.db.settings.hideMinimap;F.CreateMinimap();F.Render()end);y=y+34
    y=section('About this extremely official adventurer binder',y)
    paragraph('DuckMoo Services: Character Folio | v'..F.version..'\nBy DuckMoo Media')
    paragraph('Your warband has lore. Your brain has too many tabs. Keep the facts, the plans, and the "which gremlin learned Outland Blacksmithing?" answers in one binder. Log into each character to capture their sheet. Open professions to fill in expansion details. Assign tags and write notes so future you remembers the grand plan.')
    paragraph('/folio or /dmfolio opens your character. /folio roster opens the warband. /folio scan refreshes data. Times use your local time. Offline sheets show the last recorded snapshot.')
    paragraph('Concentration Planner is a separate addon. Its shortcut appears on your sheet when installed. ATT is optional: enable it and refresh opportunities on the ATT tab to record collection leads.')
    paragraph('amazon.com/author/kenzieduckmoo\nTwitch / AO3 / Threads / Instagram / TikTok / YouTube: @KenzieDuckMoo\nBlueSky: @kenzieduckmoo.bsky.social\nGNU GPL v3. See LICENSE.')
    F.content:SetHeight(y+4)
end

function F.Render()
    if not F.frame or not F.db or F.rendering then return end
    F.rendering=true;F.Layout();F.Clear();F.dynamic=true
    if F.opacitySlider and F.tab~='settings'then F.opacitySlider:Hide();F.opacityValue:Hide()end
    if F.notePanel and F.tab~='notes'then F.notePanel:Hide()end
    if F.rosterSearch and F.tab~='roster'then F.rosterSearch:Hide()end
    F.selected=F.selected or F.current;local c=F.db.characters[F.selected];local tab=F.tab or 'sheet'
    for _,v in ipairs(tabs)do F.tabButtons[v[1]]._active=tab==v[1];if tab==v[1]then F.pageTitle:SetText(v[2])end end
    F.pageContext:SetText(c and M.Plain((c.name or '?')..' - '..(c.realm or '?')..(F.selected==F.current and ' | This character'or ' | Recorded snapshot'))or 'Log into a character to start')
    F.sideContext:SetText(c and M.Plain(c.name or '?')or 'No character');F.sideRealm:SetText(c and M.Plain(c.realm or '?')or '')
    F.sideVersion:SetText('DuckMoo Media | v'..F.version)
    if tab=='roster'then F.Roster()
    elseif tab=='census'then F.Census()
    elseif c then
        if tab=='skills'then F.Skills(c)elseif tab=='reps'then F.Reps(c)elseif tab=='notes'then F.Notes(c)elseif tab=='att'then F.Collection(c)elseif tab=='settings'then F.Settings(c)else F.Sheet(c)end
    else text('Log into a character to start the folio.',8,8,F.width-16);F.content:SetHeight(50)end
    F.ApplyTheme();F.dynamic=false;F.rendering=false
    F.scroll:SetVerticalScroll(math.min(F.scroll:GetVerticalScroll(),math.max(0,F.content:GetHeight()-F.viewportHeight)))
end

