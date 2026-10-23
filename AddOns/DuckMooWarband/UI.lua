local _,W=...
local M=W.Model
W.TransFlag={{91/255,206/255,250/255},{245/255,169/255,184/255},{1,1,1},{245/255,169/255,184/255},{91/255,206/255,250/255}}
W.Themes={
 purple={name='DuckMoo Purple',bg={.065,.04,.09},panel={.105,.07,.14},button={.20,.12,.28},hover={.30,.19,.41},accent={.72,.45,1},text={.96,.92,1},muted={.73,.65,.83}},
 gunmetal={name='Gunmetal',bg={.075,.078,.11},panel={.13,.135,.18},button={.18,.18,.25},hover={.24,.23,.33},accent={.65,.53,.89},text={.94,.94,.98},muted={.69,.71,.80}},
 plum={name='Classic plum',bg={36/255,19/255,34/255},sidebar={50/255,27/255,48/255},panel={57/255,32/255,57/255},button={87/255,49/255,73/255},hover={115/255,65/255,94/255},accent={231/255,169/255,202/255},text={255/255,240/255,250/255},muted={226/255,195/255,216/255}},
 light={name='Light mode - warm pastels',bg={247/255,214/255,172/255},sidebar={241/255,195/255,173/255},panel={255/255,233/255,181/255},button={242/255,188/255,180/255},hover={227/255,173/255,203/255},accent={166/255,77/255,89/255},text={70/255,40/255,44/255},muted={89/255,57/255,61/255}},
 blizzard={name='Azeroth',bg={.055,.055,.06},panel={.10,.10,.11},button={.19,.15,.08},hover={.30,.24,.12},accent={.9,.72,.32},text={1,.94,.80},muted={.70,.66,.56}},
 trans={name='Trans pride',bg={91/255,206/255,250/255},sidebar={245/255,169/255,184/255},panel={245/255,169/255,184/255},button={91/255,206/255,250/255},hover={245/255,169/255,184/255},accent={255/255,255/255,255/255},text={14/255,19/255,31/255},muted={36/255,48/255,64/255},stripes=W.TransFlag},
 translight={name='Trans pride - dusk',bg={22/255,47/255,66/255},sidebar={64/255,38/255,54/255},panel={35/255,72/255,97/255},button={97/255,54/255,71/255},hover={117/255,66/255,86/255},accent={255/255,255/255,255/255},text={255/255,255/255,255/255},muted={226/255,211/255,222/255},stripes=W.TransFlag},
 lesbian={name='Lesbian pride',bg={.12,.055,.09},panel={.19,.075,.13},button={.32,.11,.22},hover={.43,.15,.30},accent={1,.54,.30},text={1,.94,.96},muted={.94,.65,.77},stripes={{.84,.18,.02},{1,.60,.32},{1,1,1},{.82,.38,.64},{.64,.02,.38}}},
 teal={name='Moonlit teal',bg={.035,.09,.10},panel={.055,.14,.16},button={.09,.24,.25},hover={.13,.32,.34},accent={.30,.85,.80},text={.90,1,.98},muted={.59,.78,.76}},
 crimson={name='Crimson',bg={.09,.03,.035},panel={.15,.045,.055},button={.26,.07,.10},hover={.37,.11,.14},accent={.94,.32,.40},text={1,.93,.92},muted={.81,.61,.61}},
 blue={name='Arcane blue',bg={.035,.055,.11},panel={.055,.085,.17},button={.09,.16,.30},hover={.14,.23,.40},accent={.39,.66,1},text={.94,.97,1},muted={.63,.73,.87}},
}
local accent={.72,.45,1,1}
local function theme()return W.Themes[W.db and W.db.settings.theme or'purple']or W.Themes.purple end
W.surfaces={};W.themeTexts={};W.inputs={}
function W.ApplyTheme()
 local t=theme()
 for _,f in ipairs(W.surfaces)do
  local c=f._themeButton and(f._active and t.hover or t.button)or f._sidebar and(t.sidebar or t.panel)or f==W.frame and t.bg or t.panel
  f:SetBackdropColor(c[1],c[2],c[3],1);f:SetBackdropBorderColor(t.accent[1],t.accent[2],t.accent[3],f._active and 1 or 0)
 end
 for _,f in ipairs(W.themeTexts)do local c=f._muted and t.muted or t.text;f:SetTextColor(c[1],c[2],c[3])end
 for _,f in ipairs(W.inputs)do f:SetTextColor(t.text[1],t.text[2],t.text[3])end
 if W.stripes then for i,f in ipairs(W.stripes)do local c=t.stripes and t.stripes[i]or t.accent;f:SetVertexColor(c[1],c[2],c[3],1);f:SetShown(t.stripes~=nil or i==1)end end
end

local unpack=unpack or table.unpack
local weekdays={'Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'}
local cadence={once='One time',daily='Daily reset',weekly='Weekly reset',weekday='On a weekday',interval='Days after completion'}
-- gsub also returns a replacement count. Native UI calls need only the text.
local function plain(s)return (tostring(s or ''):gsub('|','||'))end
local function roundSurface(f)
    if f._round then return end
    f._round={};W.surfaces[#W.surfaces+1]=f
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
        local t=texture();t:SetTexture('Interface/AddOns/DuckMooWarband/Media/Corner.tga');t:SetSize(radius,radius);t:SetPoint(c[1],c[2],c[3]);t:SetTexCoord(c[4],c[5],c[6],c[7])
    end
    -- Plain EditBoxes use our textures and have no BackdropTemplate methods.
    if f.SetBackdrop then f:SetBackdrop(nil) end
    f.SetBackdropColor=function(self,r,g,b,a)
        self._surfaceColor={r,g,b,a or 1}
        for _,t in ipairs(self._round) do t:SetVertexColor(r,g,b,a or 1) end
    end
    local accent=f:CreateTexture(nil,'BORDER');accent:SetTexture('Interface/Buttons/WHITE8X8');accent:SetWidth(2)
    accent:SetPoint('TOPLEFT',1,-6);accent:SetPoint('BOTTOMLEFT',1,6);f._accent=accent
    f.SetBackdropBorderColor=function(self,r,g,b,a) self._accent:SetVertexColor(r,g,b,a or 1) end
end
local function surface(kind,name,parent)
    local f=CreateFrame(kind,name,parent,'BackdropTemplate')
    roundSurface(f);local t=theme();f:SetBackdropColor(t.panel[1],t.panel[2],t.panel[3],1);f:SetBackdropBorderColor(t.accent[1],t.accent[2],t.accent[3],0)
    if parent==UIParent then f:SetToplevel(true);f:SetFlattensRenderLayers(true)end
    f:EnableMouse(true)
    return f
end
local function label(parent,text,x,y,width,font)
    local f=parent:CreateFontString(nil,'OVERLAY',font or 'GameFontHighlightSmall')
    f:SetPoint('TOPLEFT',x,y);f:SetWidth(width);f._muted=font=='GameFontDisableSmall';W.themeTexts[#W.themeTexts+1]=f;local c=f._muted and theme().muted or theme().text;f:SetTextColor(c[1],c[2],c[3]);f:SetJustifyH('LEFT');f:SetWordWrap(false);f:SetText(text)
    return f
end
local function button(parent,text,x,y,width,fn)
    local b=surface('Button',nil,parent);b._themeButton=true;b:SetPoint('TOPLEFT',x,y);b:SetSize(width,24)
    local t=theme();b:SetBackdropColor(t.button[1],t.button[2],t.button[3],1)
    b.caption=label(b,text,4,-6,width-8);b.caption:SetJustifyH('CENTER')
    b.SetText=function(self,t)self.caption:SetText(t)end
    b:SetScript('OnClick',fn)
    b:SetScript('OnEnter',function(self)local t=theme();self:SetBackdropColor(t.hover[1],t.hover[2],t.hover[3],1)end)
    b:SetScript('OnLeave',function(self)local t=theme();local c=self._active and t.hover or t.button;self:SetBackdropColor(c[1],c[2],c[3],1)end)
    return b
end
local function input(parent,x,y,width)
    local f=CreateFrame('EditBox',nil,parent);roundSurface(f);f:SetFontObject('GameFontHighlightSmall');f:SetTextInsets(8,8,0,0);W.inputs[#W.inputs+1]=f;local c=theme().text;f:SetTextColor(c[1],c[2],c[3]);f:SetPoint('TOPLEFT',x,y);f:SetSize(width,24)
    f:SetAutoFocus(false);f:SetMaxLetters(500);f:SetScript('OnEscapePressed',function(self)self:ClearFocus()end)
    return f
end
local function dialog(name,width,height)
    local f=surface('Frame',name,UIParent);f:SetSize(width,height);f:SetPoint('CENTER');f:SetFrameStrata('DIALOG');f:SetClampedToScreen(true)
    table.insert(UISpecialFrames,name)
    button(f,'X',width-34,-8,24,function()f:Hide()end);return f
end
function W.Choose(title,options,callback,multi)
    local f=W.choice
    if not f then
        f=dialog('DuckMooWarbandChooser',440,405);W.choice=f
        f.title=label(f,'',12,-14,380,'GameFontNormalLarge');f.rows={}
        for i=1,12 do f.rows[i]=button(f,'',12,-44-(i-1)*25,416,function()end)end
        button(f,'Previous',12,-353,85,function()f.page=math.max(1,f.page-1);f.draw()end)
        button(f,'Next',343,-353,85,function()f.page=math.min(f.pages,f.page+1);f.draw()end)
        f.status=label(f,'',112,-360,215)
        button(f,'Close',170,-378,100,function()f:Hide()end)
        f.draw=function()
            f.pages=math.max(1,math.ceil(#f.options/12))
            for i,b in ipairs(f.rows)do
                local item=f.options[(f.page-1)*12+i];b:SetShown(item~=nil)
                if item then
                    b:SetText((f.multi and (item.checked and '[x] ' or '[ ] ') or '')..plain(item.name))
                    b:SetScript('OnClick',function()
                        if f.multi then item.checked=not item.checked;f.callback(item.id,item.checked);f.draw()
                        else f:Hide();f.callback(item.id)end
                    end)
                end
            end
            f.status:SetText('Page '..f.page..' / '..f.pages)
        end
    end
    f.title:SetText(title);f.options=options;f.callback=callback;f.multi=multi;f.page=1;f:Show();f.draw()
end
local function characterOptions(selected)
    local out={}
    for guid,c in pairs(W.db.characters)do out[#out+1]={id=guid,name=(c.name or '?')..' - '..(c.realm or '?'),checked=selected and selected[guid]}end
    table.sort(out,function(a,b)return a.name<b.name end);return out
end
function W.ScopeText(task)
    if task.scope=='all' then return 'All recorded characters' end
    if task.scope=='class' then return 'Class: '..(task.rule or 'choose a class') end
    if task.scope=='group' then return 'Group: '..(task.rule or 'choose a group') end
    if task.scope=='armor' then return 'Armor: '..(task.rule or 'choose armor') end
    if task.scope=='covenant' then
        for _,c in pairs(W.db.characters)do if c.covenantID==task.rule and c.covenantName then return 'Covenant: '..c.covenantName end end
        return 'Covenant: '..tostring(task.rule or 'choose covenant')
    end
    local count=0;local name
    for guid,yes in pairs(task.characters or {})do if yes then count=count+1;local c=W.db.characters[guid];name=c and c.name or 'Unknown character' end end
    return count==1 and name or (count..' selected characters')
end
function W.EditTask(task)
    local f=W.editor
    if not f then
        f=dialog('DuckMooWarbandEditor',580,435);W.editor=f
        label(f,'TASK DETAILS',14,-14,500,'GameFontNormalLarge')
        label(f,'What would you like to do?',14,-48,540)
        f.text=input(f,22,-70,532)
        label(f,'Applies to',14,-106,265);label(f,'Character or rule',298,-106,265)
        f.scope=button(f,'',14,-128,266,function()
            W.Choose('Applies to',{{id='selected',name='Selected characters'},{id='all',name='All recorded characters'},{id='class',name='Characters of a class'},{id='group',name='A custom character group'},{id='armor',name='Primary armor category'},{id='covenant',name='Recorded active covenant'}},function(id)f.draft.scope=id;f.draft.rule=nil;f.refresh()end)
        end)
        f.rule=button(f,'',298,-128,266,function()
            local d=f.draft
            if d.scope=='selected' then
                W.Choose('Choose characters',characterOptions(d.characters),function(id,yes)d.characters[id]=yes or nil;f.refresh()end,true)
            elseif d.scope=='class' then
                local options={};local seen={}
                for _,c in pairs(W.db.characters)do if c.class and not seen[c.class]then options[#options+1]={id=c.class,name=c.className or c.class};seen[c.class]=true end end
                table.sort(options,function(a,b)return a.name<b.name end)
                W.Choose('Choose a recorded class',options,function(id)d.rule=id;f.refresh()end)
            elseif d.scope=='armor' then
                W.Choose('Primary armor category',{{id='Cloth',name='Cloth'},{id='Leather',name='Leather'},{id='Mail',name='Mail'},{id='Plate',name='Plate'}},function(id)d.rule=id;f.refresh()end)
            elseif d.scope=='covenant' then
                local options={};local seen={}
                for _,c in pairs(W.db.characters)do if c.covenantID and c.covenantID>0 and not seen[c.covenantID]then options[#options+1]={id=c.covenantID,name=c.covenantName or ('Covenant '..c.covenantID)};seen[c.covenantID]=true end end
                table.sort(options,function(a,b)return a.name<b.name end)
                if #options==0 then f.status:SetText('No active covenant recorded yet. Log into a character with an active covenant.');return end
                W.Choose('Recorded active covenant',options,function(id)d.rule=id;f.refresh()end)
            elseif d.scope=='group' then
                local options={};local seen={}
                for _,c in pairs(W.db.characters)do for name in pairs(c.groups or {})do if not seen[name]then options[#options+1]={id=name,name=name};seen[name]=true end end end
                table.sort(options,function(a,b)return a.name<b.name end)
                if #options==0 then f.status:SetText('Create a group using the Characters button first.');return end
                W.Choose('Choose a group',options,function(id)d.rule=id;f.refresh()end)
            end
        end)
        label(f,'Progress',14,-169,540)
        f.progress=button(f,'',14,-190,550,function()f.draft.progress=f.draft.progress=='account' and 'character' or 'account';f.refresh()end)
        label(f,'Appears',14,-230,265);label(f,'Weekday or interval days',298,-230,265)
        f.repeatButton=button(f,'',14,-251,266,function()
            W.Choose('Appears',{{id='once',name='One time; stays until handled'},{id='daily',name='Every daily game reset'},{id='weekly',name='Every weekly game reset'},{id='weekday',name='Only on a chosen weekday'},{id='interval',name='Days after completion'}},function(id)f.draft.repeatMode=id;f.refresh()end)
        end)
        f.dayButton=button(f,'',298,-251,266,function()
            local options={};for i,name in ipairs(weekdays)do options[#options+1]={id=i,name=name}end
            W.Choose('Choose a weekday',options,function(id)f.draft.weekday=id;f.refresh()end)
        end)
        f.interval=input(f,306,-251,245);f.interval:SetMaxLetters(3)
        label(f,'Category (optional)',14,-293,540);f.category=input(f,22,-315,532);f.category:SetMaxLetters(80)
        f.status=label(f,'',14,-351,550);f.status:SetWordWrap(true);f.status:SetHeight(35)
        button(f,'Save',14,-396,120,function()
            f.draft.text=f.text:GetText();f.draft.category=f.category:GetText();f.draft.interval=tonumber(f.interval:GetText())
            local saved,err=W.SaveTask(f.draft,f.id)
            if saved then f:Hide();W.Render()else f.status:SetText(err)end
        end)
        button(f,'Cancel',444,-396,120,function()f:Hide()end)
        f.refresh=function()
            local d=f.draft
            f.scope:SetText(({selected='Selected characters',all='All recorded characters',class='By class',group='By group',armor='By armor',covenant='By covenant'})[d.scope])
            f.rule:SetText(plain(W.ScopeText(d)));f.rule:SetEnabled(d.scope~='all')
            f.progress:SetText(d.progress=='account' and 'Once for the account (shared completion)' or 'Separately for each eligible character')
            f.repeatButton:SetText(cadence[d.repeatMode]);f.dayButton:SetShown(d.repeatMode=='weekday');f.interval:SetShown(d.repeatMode=='interval')
            f.dayButton:SetText(weekdays[d.weekday or 1])
        end
    end
    f.id=task and task.id
    f.draft=M.Copy(task or {text='',category='',scope='selected',characters={[W.current]=true},progress='character',repeatMode='once',weekday=1,interval=4})
    f.draft.characters=f.draft.characters or {};f.text:SetText(f.draft.text);f.category:SetText(f.draft.category or '')
    f.interval:SetText(tostring(f.draft.interval or 4));f.status:SetText('Changes to cadence start a new occurrence; prior activity remains recorded.')
    f:Show();f.refresh()
end
function W.ManageCharacter(guid)
    local f=W.characterEditor
    if not f then
        f=dialog('DuckMooWarbandGroups',470,160);W.characterEditor=f
        f.title=label(f,'',14,-14,400,'GameFontNormalLarge')
        label(f,'Groups, separated by commas (for example: Crafters, Weekend)',14,-48,440)
        f.edit=input(f,22,-72,426)
        button(f,'Save groups',14,-119,130,function()
            local groups={};for part in f.edit:GetText():gmatch('[^,]+')do local name=M.Trim(part):lower();if name~='' then groups[name]=true end end
            W.db.characters[f.guid].groups=groups;f:Hide();W.Render()
        end)
        button(f,'Cancel',356,-119,100,function()f:Hide()end)
    end
    f.guid=guid;local c=W.db.characters[guid];local names={};for name in pairs(c.groups)do names[#names+1]=name end;table.sort(names)
    f.title:SetText(plain(c.name..' - '..c.realm));f.edit:SetText(table.concat(names,', '));f:Show()
end
function W.CategoryEditor(category)
    local f=W.categoryEditor
    if not f then
        f=dialog('DuckMooWarbandCategory',490,190);W.categoryEditor=f
        f.title=label(f,'',14,-14,430,'GameFontNormalLarge')
        label(f,'Show unfinished tasks in this category on these local weekdays:',14,-47,460)
        f.days={}
        for i,name in ipairs(weekdays)do
            f.days[i]=button(f,'',14+(i-1)*66,-72,61,function()f.selected[i]=not f.selected[i] or nil;f.refresh()end)
        end
        f.status=label(f,'',14,-108,460)
        button(f,'Every day',14,-146,100,function()W.db.categoryRules[f.category]=nil;f:Hide();W.Render()end)
        button(f,'Save days',376,-146,100,function()W.db.categoryRules[f.category]={days=M.Copy(f.selected)};f:Hide();W.Render()end)
        f.refresh=function()
            local count=0
            for i,b in ipairs(f.days)do b:SetText((f.selected[i] and '[x] ' or '')..weekdays[i]:sub(1,3));if f.selected[i]then count=count+1 end end
            f.status:SetText(count==0 and 'No days selected: this category stays hidden from Today.' or 'This controls visibility; it does not complete or skip tasks.')
        end
    end
    f.category=category;f.title:SetText('Category: '..plain(category~='' and category or 'Uncategorized'))
    local rule=W.db.categoryRules[category]
    f.selected=M.Copy(rule and rule.days or {true,true,true,true,true,true,true});f:Show();f.refresh()
end
function W.CategoryPicker()
    local names={['']=true};for _,task in pairs(W.db.tasks)do names[task.category or '']=true end
    for name in pairs(W.db.categoryRules)do names[name]=true end
    local options={};for name in pairs(names)do options[#options+1]={id=name,name=name~='' and name or 'Uncategorized'}end
    table.sort(options,function(a,b)return a.name<b.name end)
    W.Choose('Category visibility',options,W.CategoryEditor)
end
function W.CreateUI()
    if W.frame then return end
    local f=surface('Frame','DuckMooWarbandFrame',UIParent);W.frame=f;f:SetClampedToScreen(true)
    f:SetFrameStrata('HIGH');f:SetResizable(true)
    local pos=W.db.settings.position;f:SetPoint(pos and pos.point or 'CENTER',UIParent,pos and pos.relativePoint or 'CENTER',pos and pos.x or 0,pos and pos.y or 0)
    f:SetMovable(true);f:EnableMouse(true);f:RegisterForDrag('LeftButton')
    f:SetScript('OnDragStart',function(self)self:StartMoving()end)
    f:SetScript('OnDragStop',function(self)self:StopMovingOrSizing();local point,_,relativePoint,x,y=self:GetPoint();W.SaveGeometry()end)
    table.insert(UISpecialFrames,'DuckMooWarbandFrame')
    f.title=label(f,'WARBAND PLANNER',12,-12,350,'GameFontNormalLarge')
    f.close=button(f,'X',0,0,24,function()f:Hide()end)
    f.mode=button(f,'Compact',12,-40,95,function()W.SetCompact(not W.db.settings.compact)end)
    f.view=button(f,'All tasks',113,-40,95,function()W.manage=not W.manage;W.page=1;W.Render()end)
    f.group=button(f,'By character',214,-40,114,function()W.db.settings.byActivity=not W.db.settings.byActivity;W.page=1;W.Render()end)
    f.undo=button(f,'Undo',334,-40,75,function()M.Undo(W.db);W.Render()end)
    f.captureLabel=label(f,'',12,-75,600)
    f.capture=input(f,20,-94,320)
    f.captureHint=label(f.capture,'Add one small next step…',8,-6,280,'GameFontDisableSmall')
    f.capture:SetScript('OnTextChanged',function(self)f.captureHint:SetShown(self:GetText()=='')end)
    f.add=button(f,'Add',0,0,60,function()
        local task,err=W.Quick(f.capture:GetText())
        if task then
            f.capture:SetText('');W.page=1
            if not W.db.settings.compact then W.view='today';W.manage=false;W.filter='';if f.search then f.search:SetText('')end end
            W.Render()
        else W.Print(err)end
    end)
    f.capture:SetScript('OnEnterPressed',function()f.add:GetScript('OnClick')()end)
    f.details=button(f,'Details',0,0,70,function()W.EditTask()end)
    f.characters=button(f,'Characters',12,-127,95,function()W.Choose('Recorded characters: edit groups',characterOptions(),W.ManageCharacter)end)
    f.categories=button(f,'Categories',113,-127,95,W.CategoryPicker)
    f.packs=button(f,'Starter tasks',214,-127,100,function()
        W.Choose('Optional manual reminders for this character',{{id='daily',name='Daily world activities (1 task)'},{id='weekly',name='Weekly activities (3 tasks)'}},function(id)
            local count,err=W.AddStarterPack(id)
            W.Print(count and (count..' reminders added. Edit or archive anything you do not want.') or err);W.Render()
        end)
    end)
    f.status=label(f,'',224,-133,500)
    f.rows={}
    for i=1,12 do
        local row=surface('Frame',nil,f);row.title=label(row,'',8,-5,400);row.detail=label(row,'',8,-23,400,'GameFontDisableSmall')
        row.done=button(row,'Done',0,0,54,function()end);row.more=button(row,'...',0,0,28,function()end)
        f.rows[i]=row
    end
    f.previous=button(f,'<',0,0,30,function()W.page=math.max(1,(W.page or 1)-1);W.Render()end)
    f.next=button(f,'>',0,0,30,function()W.page=(W.page or 1)+1;W.Render()end)
    f.pageLabel=label(f,'',12,0,350);f.empty=label(f,'',12,-167,620);f.empty:SetWordWrap(true);f.empty:SetHeight(60)
    W.sidebar=surface('Frame',nil,f);W.sidebar._sidebar=true;W.sidebar:SetPoint('TOPLEFT',12,-12)
    W.stripes={};for i=1,5 do local t=W.sidebar:CreateTexture(nil,'ARTWORK');t:SetTexture('Interface/Buttons/WHITE8X8');t:SetPoint('TOPLEFT',12,-10-(i-1)*4);t:SetSize(140,4);W.stripes[i]=t end
    label(W.sidebar,'DuckMoo',12,-38,140,'GameFontNormalLarge');label(W.sidebar,'WARBAND PLANNER',12,-59,140,'GameFontDisableSmall');label(W.sidebar,'YOUR WARBAND',12,-86,140,'GameFontDisableSmall')
    W.nav={};for i,v in ipairs({{'today','Today'},{'all','All tasks'},{'characters','Characters'},{'categories','Categories'},{'session','Session'},{'gold','Gold'},{'loot','Loot'},{'sessions','Session history'},{'preferences','Preferences'}})do
        local key=v[1];local b=button(W.sidebar,v[2],8,-109-(i-1)*34,148,function()if key=='session'then W.activitySession=nil end;W.SelectPage(key)end);b:SetHeight(30);W.nav[key]=b
    end
    W.sideName=label(W.sidebar,'',12,0,140,'GameFontNormal');W.sideName:ClearAllPoints();W.sideName:SetPoint('BOTTOMLEFT',12,57)
    W.sideRealm=label(W.sidebar,'',12,0,140,'GameFontDisableSmall');W.sideRealm:ClearAllPoints();W.sideRealm:SetPoint('BOTTOMLEFT',12,38)
    local version=label(W.sidebar,'v'..W.version,12,0,140,'GameFontDisableSmall');version:ClearAllPoints();version:SetPoint('BOTTOMLEFT',12,16)
    f.context=label(f,'',194,-45,500,'GameFontDisableSmall')
    W.CreateActivityUI(f)
    f.search=input(f,202,-76,600);f.search:SetMaxLetters(100)
    f.searchHint=label(f.search,'Search tasks, characters or categories',8,-6,400,'GameFontDisableSmall')
    f.search:SetScript('OnTextChanged',function(self)W.filter=self:GetText();W.page=1;W.Render()end)
    f.summary={};for i,title in ipairs({'REMAINING','CHARACTERS WITH TASKS','SHARED TASKS'})do
        local card=surface('Frame',nil,f);card.heading=label(card,title,10,-7,210,'GameFontDisableSmall');card.value=label(card,'',10,-26,210,'GameFontNormalLarge');f.summary[i]=card
    end
    f.prefs=surface('Frame',nil,f)
    label(f.prefs,'Make this planner feel like yours',14,-14,620,'GameFontNormalLarge')
    f.palette=button(f.prefs,'',14,-52,370,function()
        local options={};for id,t in pairs(W.Themes)do options[#options+1]={id=id,name=t.name}end;table.sort(options,function(a,b)return a.name<b.name end)
        W.Choose('Choose a palette',options,function(id)W.db.settings.theme=id;W.ApplyTheme();W.Render()end)
    end)
    button(f.prefs,'Refresh recorded characters',14,-92,246,function()W.CaptureCharacter();W.Render()end)
    label(f.prefs,'Quick entry starts with your current character. Organize it later through task details.',14,-136,630):SetWordWrap(true)
    label(f.prefs,'Working on a task can stay unfinished. Use Worked on it in the task menu whenever that fits.',14,-176,630):SetWordWrap(true)
    label(f.prefs,'Character information comes from recorded snapshots. Task progress is yours to mark.',14,-216,630,'GameFontDisableSmall'):SetWordWrap(true)
    f.grip=CreateFrame('Button',nil,f);f.grip:SetPoint('BOTTOMRIGHT',-1,1);f.grip:SetSize(18,18);f.grip:SetNormalTexture('Interface/ChatFrame/UI-ChatIM-SizeGrabber-Up')
    f.grip:SetScript('OnMouseDown',function(_,mouse)if mouse=='LeftButton'then W.resizing=true;f:StartSizing('BOTTOMRIGHT')end end)
    f.grip:SetScript('OnMouseUp',function()f:StopMovingOrSizing();W.resizing=false;W.SaveGeometry();W.Render()end)
    f:SetScript('OnSizeChanged',function()if not W.layoutLock and not W.rendering and not W.resizing and W.nav then W.Render()end end)
    W.view=W.db.settings.fullPage or'today';W.manage=W.view=='all';W.ApplyGeometry()
    f.elapsed=0;f:SetScript('OnUpdate',function(self,seconds)
        self.elapsed=self.elapsed+seconds
        if self.elapsed>=30 then self.elapsed=0;W.Render()end
    end)
end

local function matches(value,query)return tostring(value or''):lower():find(query,1,true)~=nil end
function W.IsActivityPage(page)return page=='session'or page=='gold'or page=='loot'or page=='sessions'end
local rangeNames={session='Current session',today='Today',week='Last 7 days',all='All saved history'}
function W.CreateActivityUI(f)
 local a=surface('Frame',nil,f);f.activity=a;a:SetPoint('TOPLEFT',194,-112);a:SetSize(818,50)
 a.range=button(a,'',8,-18,170,function()
  W.Choose('Show activity from',{{id='session',name='Current session'},{id='today',name='Today (local calendar day)'},{id='week',name='Last 7 calendar days'},{id='all',name='All saved history (up to 100 sessions)'}},function(id)W.activityRange=id;W.page=1;W.Render()end)
 end)
 a.character=button(a,'',186,-18,236,function()
  local options={{id='all',name='All recorded characters'}}
  for guid,c in pairs(W.db.characters)do options[#options+1]={id=guid,name=(c.name or'?')..' - '..(c.realm or'?')}end
  table.sort(options,function(x,y)if x.id==y.id then return false elseif x.id=='all'then return true elseif y.id=='all'then return false end;return x.name<y.name end)
  W.Choose('Filter by character',options,function(id)W.activityCharacter=id~='all'and id or nil;W.page=1;W.Render()end)
 end)
 a.name=input(a,8,-18,360);a.hint=label(a.name,'Name this session (optional)',8,-6,330,'GameFontDisableSmall')
 a.name:SetScript('OnTextChanged',function(self)a.hint:SetShown(self:GetText()=='')end)
 a.save=button(a,'Save name',376,-18,92,function()
  local s=W.Activity.Get(W.activitySession);if s then s.label=M.Trim(a.name:GetText()):sub(1,120);W.Render()end
 end)
 a.new=button(a,'New session',0,0,110,function()W.Activity.Begin();W.activitySession=nil;W.page=1;W.Render()end)
 a.new:ClearAllPoints();a.new:SetPoint('TOPRIGHT',-8,-18)
 a.live=button(a,'Live session',0,0,110,function()W.activitySession=nil;W.page=1;W.Render()end)
 a.live:ClearAllPoints();a.live:SetPoint('TOPRIGHT',-126,-18)
 f.activityNote=label(a,'',8,8,800,'GameFontDisableSmall')
end
local function shortMoney(value)return W.Activity.Money(value,true)end
function W.ActivityRows(page,query)
 local A=W.Activity;local data=A.Init();local rows={};local headings,values,note
 local selected=A.Get(W.activitySession)
 if page=='session'then
  local value,why=A.Cash(selected);local estimate,unknown=A.Estimate(selected)
  headings={'OBSERVED CASH CHANGE','ITEMS RECEIVED','VENDOR ESTIMATE'}
  values={value and shortMoney(value)or'Incomplete',tostring(selected and selected.quantity or 0),A.Money(estimate)..(unknown>0 and' + ?'or'')}
  note=selected and(A.Character(selected.character)..' | '..A.Duration(selected)..' | '..(selected.endedAt and'Saved session'or'Live session'))or'Your session starts automatically when you enter the world.'
  if selected then
   rows[#rows+1]={title='Wallet: '..A.Money(selected.walletEnd)..' | change '..shortMoney(selected.walletDelta),detail='Increases '..A.Money(selected.walletIn)..' | decreases '..A.Money(selected.walletOut)..' | includes transfers',tip=why}
   rows[#rows+1]={title='Warbank: '..A.Money(selected.bankEnd)..' | change '..shortMoney(selected.bankDelta),detail='Observed changes only; deposits move gold between balances.',tip='Cash change combines wallet and bank changes. It is not a profit calculation.'}
   for i=#selected.events,1,-1 do
    local e=selected.events[i];local cash=e.amount~=nil
    rows[#rows+1]={title=cash and(e.title..': '..shortMoney(e.amount))or(e.title..' x'..e.quantity),detail=date('%H:%M',e.at)..' | '..(cash and'Actual balance change'or(e.kind=='crafted'and'Crafted item'or e.kind=='received'and'Received item'or'Looted item')),link=e.link}
   end
   if selected.trimmedEvents then rows[#rows+1]={title='Earlier event details condensed',detail=selected.trimmedEvents..' older events omitted; session totals retained.'}end
   if unknown>0 then rows[#rows+1]={title=unknown..' items have no recorded vendor price',detail='Known vendor values are estimates only. No auction value is inferred.'}end
   if selected.walletGap or selected.bankGap then rows[#rows+1]={title='Some balance reads were unavailable',detail='Cash coverage is incomplete. Unobserved changes are not guessed.'}end
  end
 elseif page=='gold'then
  local total,count=0,0
  for guid,snapshot in pairs(data.wallets)do
   total=total+snapshot.amount;count=count+1
   rows[#rows+1]={title=A.Character(guid)..' | '..A.Money(snapshot.amount),detail='Wallet snapshot | '..date('%b %d, %H:%M',snapshot.at)..(guid==W.current and' | current character'or' | offline snapshot')}
  end
  table.sort(rows,function(x,y)return x.title<y.title end)
  if data.bank then table.insert(rows,1,{title='Warbank | '..A.Money(data.bank.amount),detail='Account bank snapshot | '..date('%b %d, %H:%M',data.bank.at)})end
  headings={'WARBANK SNAPSHOT','CURRENT WALLET','RECORDED WALLETS'}
  values={A.Money(data.bank and data.bank.amount),A.Money(data.wallets[W.current]and data.wallets[W.current].amount),A.Money(total)}
  note=count..' wallet snapshots; excludes unrecorded characters. Offline balances may have changed.'
 else
  local list,cutoff=A.Filtered(page=='sessions'and'all'or'session');local quantity,value,unknown,sessions=0,0,0,0;local items={}
  for _,s in ipairs(list)do
   if page=='loot'then
    for _,item in pairs(s.items)do
     if not cutoff or item.at>=cutoff then
      local key=item.link..':'..item.kind;local row=items[key]
      if not row then row={name=item.name,link=item.link,kind=item.kind,quantity=0,value=0,unknown=0};items[key]=row end
      row.quantity=row.quantity+item.quantity;quantity=quantity+item.quantity
      if item.price~=nil then local price=item.price*item.quantity;row.value=row.value+price;value=value+price
      else row.unknown=row.unknown+item.quantity;unknown=unknown+item.quantity end
     end
    end
    for day,count in pairs(s.unlistedDays or{})do if not cutoff or day>=date('%Y-%m-%d',cutoff)then unknown=unknown+count;quantity=quantity+count end end
   elseif not cutoff or s.startedAt>=cutoff then
    sessions=sessions+1;quantity=quantity+s.quantity;local cash=A.Cash(s)
    rows[#rows+1]={title=(s.label~=''and s.label or A.Character(s.character))..' | '..(cash and shortMoney(cash)or'Cash coverage incomplete'),detail=date('%b %d, %H:%M',s.startedAt)..' | '..A.Duration(s)..' | '..s.quantity..' items | '..A.Character(s.character),session=s.id,tip=s.interrupted and'Client ended unexpectedly; duration stops at the last observation.'or nil}
   end
  end
  if page=='loot'then
   local distinct=0;for _,item in pairs(items)do
    distinct=distinct+1;rows[#rows+1]={title=item.name..' x'..item.quantity,detail=(item.kind=='crafted'and'Crafted'or item.kind=='received'and'Received'or'Looted')..' | vendor estimate '..A.Money(item.value)..(item.unknown>0 and' | '..item.unknown..' unpriced'or''),link=item.link}
   end
   table.sort(rows,function(x,y)return x.title<y.title end)
   headings={'ITEM GROUPS','ITEMS RECEIVED','VENDOR ESTIMATE'};values={tostring(distinct),tostring(quantity),A.Money(value)..(unknown>0 and' + ?'or'')}
   note='Vendor estimates are not gold earned. Crafted and received items are labelled separately.'
  else
   -- Sessions are appended chronologically, so reverse for newest first.
   local reversed={};for i=#rows,1,-1 do reversed[#reversed+1]=rows[i]end;rows=reversed
   headings={'SAVED SESSIONS','ITEMS RECEIVED','HISTORY LIMIT'};values={tostring(sessions),tostring(quantity),'100 sessions'}
   note='Choose View to revisit a session. Date filters use the session start time.'
  end
 end
 local filtered={};for _,r in ipairs(rows)do if matches(r.title..' '..r.detail,query)then filtered[#filtered+1]=r end end
 return filtered,headings,values,note,selected
end
function W.RenderActivity(page,query,left,bodyWidth)
 local f=W.frame;local a=f.activity;local A=W.Activity
 f.capture:Hide();f.captureLabel:Hide();f.add:Hide();f.details:Hide();f.group:Hide();f.undo:Hide();f.packs:Hide();f.prefs:Hide()
 f.search:SetWidth(bodyWidth-16);f.searchHint:SetText('Search this activity page')
 local rows,headings,values,note,selected=W.ActivityRows(page,query);W.visibleRows=rows
 a:SetWidth(bodyWidth);f.activityNote:SetWidth(bodyWidth-16);f.activityNote:SetText(plain(note))
 local session=page=='session';local filters=page=='loot'or page=='sessions'
 a.name:SetShown(session and selected~=nil);a.hint:SetShown(session and selected~=nil and a.name:GetText()=='');a.save:SetShown(session and selected~=nil)
 a.new:SetShown(session or page=='gold');a.new:SetText(page=='gold'and'Refresh balances'or'New session')
 a.new:SetScript('OnClick',function()if page=='gold'then A.Sample()else A.Begin();W.activitySession=nil;W.page=1 end;W.Render()end)
 a.live:SetShown(session and W.activitySession~=nil)
 a.range:SetShown(filters);a.character:SetShown(filters)
 a.range:SetText(rangeNames[W.activityRange or(page=='sessions'and'all'or'session')]);a.character:SetText(W.activityCharacter and plain(A.Character(W.activityCharacter))or'All recorded characters')
 if session and selected and a.loadedSession~=selected.id then a.loadedSession=selected.id;a.name:SetText(selected.label)end
 for i,card in ipairs(f.summary)do
  card:Show();card:ClearAllPoints();card:SetPoint('TOPLEFT',left+(i-1)*((bodyWidth-16)/3+8),-175);card:SetSize((bodyWidth-16)/3,51)
  card.heading:SetWidth((bodyWidth-16)/3-20);card.value:SetWidth((bodyWidth-16)/3-20);card.value:SetFontObject('GameFontHighlight');card.heading:SetText(headings[i]);card.value:SetText(values[i])
 end
 W.pageSize=math.max(1,math.min(12,math.floor((f:GetHeight()-326)/58)))
 local pages=math.max(1,math.ceil(#rows/W.pageSize));W.page=math.max(1,math.min(W.page or 1,pages))
 f.status:Show();f.status:ClearAllPoints();f.status:SetPoint('TOPLEFT',left,-243);f.status:SetWidth(bodyWidth)
 f.status:SetText(page=='session'and'Recent activity — balance changes include transfers'or page=='gold'and'Balances are snapshots; no automatic deposits or withdrawals'or page=='loot'and'Items received from observed self-loot messages'or'Saved sessions from this addon; no external history imported')
 for i,row in ipairs(f.rows)do
  local r=i<=W.pageSize and rows[(W.page-1)*W.pageSize+i]or nil;row:SetShown(r~=nil)
  if r then
   row:ClearAllPoints();row:SetPoint('TOPLEFT',left,-278-(i-1)*58);row:SetSize(bodyWidth,52)
   row.title:SetWidth(bodyWidth-106);row.detail:SetWidth(bodyWidth-106);row.title:SetFontObject('GameFontHighlight');row.title:SetText(plain(r.title));row.detail:Show();row.detail:SetText(plain(r.detail));row.more:Hide()
   row.done:SetShown(r.session~=nil);row.done:SetText('View');row.done:ClearAllPoints();row.done:SetPoint('TOPRIGHT',-12,-13);row.done:SetWidth(78)
   row.done:SetScript('OnClick',function()W.activitySession=r.session;W.SelectPage('session')end)
   row:SetScript('OnEnter',function(self)
    GameTooltip:SetOwner(self,'ANCHOR_RIGHT')
    if r.link and GameTooltip.SetHyperlink then GameTooltip:SetHyperlink(r.link)else GameTooltip:SetText(plain(r.title))end
    GameTooltip:AddLine(plain(r.detail),1,1,1,true)
    if r.tip then GameTooltip:AddLine(plain(r.tip),1,1,1,true)end
    GameTooltip:Show()
   end);row:SetScript('OnLeave',function()GameTooltip:Hide()end)
  end
 end
 f.empty:SetShown(#rows==0);f.empty:ClearAllPoints();f.empty:SetPoint('TOPLEFT',left+4,-286);f.empty:SetWidth(bodyWidth-8)
 f.empty:SetText(query~=''and'No matches. Clear the search to see this page.'or'Nothing recorded for this selection yet. Play normally; activity is captured while this addon is enabled.')
 local bottom=f:GetHeight()-30
 f.pageLabel:Show();f.pageLabel:ClearAllPoints();f.pageLabel:SetPoint('TOPLEFT',left,-bottom-6);f.pageLabel:SetWidth(bodyWidth-100);f.pageLabel:SetText('Page '..W.page..' / '..pages..' | v'..W.version)
 f.previous:Show();f.next:Show();f.previous:ClearAllPoints();f.previous:SetPoint('TOPRIGHT',-76,-bottom);f.next:ClearAllPoints();f.next:SetPoint('TOPRIGHT',-40,-bottom);f.previous:SetEnabled(W.page>1);f.next:SetEnabled(W.page<pages)
end
local function rowName(row)
    if row.key=='@account' then return 'Account' end
    local c=W.db.characters[row.key];return (row.key==W.current and '* ' or '')..(c and (c.name..' - '..c.realm) or 'Unknown')
end
function W.SaveGeometry()
    local f=W.frame;local key=W.db.settings.compact and 'compact' or 'full'
    W.db.settings[key..'Size']={f:GetWidth(),f:GetHeight()}
    local a,_,b,x,y=f:GetPoint();W.db.settings[key..'Position']={point=a,relativePoint=b,x=x,y=y}
end
function W.ApplyGeometry()
    local f,s=W.frame,W.db.settings;local compact=s.compact;local key=compact and 'compact' or 'full'
    local size=s[key..'Size']or(compact and{450,300}or{1040,740})
    local pos=s[key..'Position']or s.position
    W.layoutLock=true
    local minW,minH=compact and 340 or 940,compact and 200 or 560
    local screenW,screenH=UIParent:GetWidth()or 1920,UIParent:GetHeight()or 1080
    local maxW,maxH=math.max(minW,screenW-30),math.max(minH,screenH-30)
    f:SetResizeBounds(minW,minH,maxW,maxH)
    f:SetSize(math.min(maxW,math.max(minW,size[1])),math.min(maxH,math.max(minH,size[2])))
    f:SetScale(math.min(1,(screenW-30)/f:GetWidth(),(screenH-30)/f:GetHeight()))
    f:ClearAllPoints();f:SetPoint(pos and pos.point or'CENTER',UIParent,pos and pos.relativePoint or'CENTER',pos and pos.x or 0,pos and pos.y or 0)
    W.layoutLock=false
end
function W.SetCompact(value)
    if W.db.settings.compact==value then return end
    W.SaveGeometry();W.db.settings.compact=value;W.page=1;W.ApplyGeometry();W.Render()
end
function W.SelectPage(key)
    W.view=key;W.manage=key=='all';W.page=1;W.filter='';W.frame.search:SetText('')
    if W.db.settings.compact then W.SetCompact(false)end
    W.Render()
end
function W.Page()
    if not W.db.settings.compact and(W.view=='characters'or W.view=='categories'or W.view=='preferences'or W.IsActivityPage(W.view))then return W.view end
    return W.manage and'all'or'today'
end
function W.DirectoryRows(page,query)
    local out={}
    if page=='characters'then
        for guid,c in pairs(W.db.characters)do
            local groups={};for name in pairs(c.groups or{})do groups[#groups+1]=name end;table.sort(groups)
            local text=(c.name or'?')..' - '..(c.realm or'?');local groupText=table.concat(groups,', ')
            if matches(text..' '..groupText..' '..(c.className or c.class or'')..' '..(c.covenantName or''),query)then
                out[#out+1]={id=guid,title=(guid==W.current and '* 'or'')..text,detail=(c.className or c.class or'Unknown class')..' | '..(groupText~=''and groupText or'No groups assigned'),character=c}
            end
        end
    else
        local names={['']=0};for _,task in pairs(W.db.tasks)do local name=task.category or'';names[name]=(names[name]or 0)+1 end
        for name in pairs(W.db.categoryRules)do names[name]=names[name]or 0 end
        for name,count in pairs(names)do
            local title=name~=''and name or'Uncategorized';local rule=W.db.categoryRules[name];local days={}
            if rule then for i,v in ipairs(weekdays)do if rule.days[i]then days[#days+1]=v:sub(1,3)end end end
            local timing=not rule and'Every day'or(#days==0 and'Hidden from Today'or table.concat(days,', '))
            if matches(title,query)then out[#out+1]={id=name,title=title,detail=timing..' | '..count..(count==1 and' saved task'or' saved tasks')}end
        end
    end
    table.sort(out,function(a,b)return a.title:lower()<b.title:lower()end);return out
end
function W.Render()
    if not W.frame or W.rendering then return end;W.rendering=true
    local f,s=W.frame,W.db.settings;local compact=s.compact;local page=W.Page()
    local width=compact and(s.compactSize and s.compactSize[1]or 450)or f:GetWidth()
    if compact then f:SetWidth(width)end
    local left=compact and 8 or 194;local bodyWidth=compact and width-16 or width-222
    local c=W.db.characters[W.current];local query=compact and''or(W.filter or''):lower()
    local tasks=page=='today'or page=='all';W.manage=page=='all'
    if not compact then s.fullPage=page end
    W.sidebar:SetShown(not compact);W.sidebar:SetSize(164,f:GetHeight()-24)
    W.sideName:SetText(plain(c and c.name or'This character'));W.sideRealm:SetText(plain(c and c.realm or''))
    for key,b in pairs(W.nav)do b._active=key==page end
    local titles={today='Today',all='All tasks',characters='Characters',categories='Categories',preferences='Preferences',session='Session',gold='Gold',loot='Loot',sessions='Session history'}
    f.title:ClearAllPoints();f.title:SetPoint('TOPLEFT',compact and 12 or 194,compact and -12 or -19);f.title:SetWidth(width-(compact and 130 or 340));f.title:SetText(compact and'Warband Planner'or titles[page])
    f.context:SetShown(not compact);f.context:SetWidth(bodyWidth-120)
    local contexts={today='A next step for every character, wherever you are logged in.',all='Task definitions, including completed and archived tasks.',characters='Recorded characters and your custom groups.',categories='Choose when each category appears in Today.',preferences='Appearance and gentle reminders, on your terms.',session='What happened while you played.',gold='Real balances, with a timestamp for every snapshot.',loot='Items you received, kept separate from actual gold.',sessions='Return to what you were doing across your characters.'}
    f.context:SetText(contexts[page])
    f.close:ClearAllPoints();f.close:SetPoint('TOPRIGHT',-12,-14)
    f.mode:ClearAllPoints();f.mode:SetPoint('TOPRIGHT',-44,-14);f.mode:SetWidth(86);f.mode:SetText(compact and'Full view'or'Compact')
    f.view:SetShown(compact);f.characters:Hide();f.categories:Hide()
    f.search:SetShown(not compact);f.searchHint:SetShown(not compact and f.search:GetText()=='');f.search:SetWidth(bodyWidth-216)
    f.activity:SetShown(not compact and W.IsActivityPage(page))
    if not compact and W.IsActivityPage(page)then W.RenderActivity(page,query,left,bodyWidth);W.ApplyTheme();W.rendering=false;return end
    f.capture:Show();f.add:Show();f.undo:Show()
    f.searchHint:SetText('Search tasks, characters or categories')
    for _,card in ipairs(f.summary)do card.value:SetFontObject('GameFontNormalLarge')end
    f.packs:SetShown(not compact);f.packs:ClearAllPoints();f.packs:SetPoint('TOPRIGHT',-28,-76)
    f.undo:ClearAllPoints();f.undo:SetPoint('TOPRIGHT',compact and -12 or -144,compact and -77 or -76);f.undo:SetEnabled(W.db.undo~=nil)
    f.captureLabel:SetShown(not compact);f.captureLabel:ClearAllPoints();f.captureLabel:SetPoint('TOPLEFT',194,-118);f.captureLabel:SetWidth(bodyWidth)
    f.captureLabel:SetText('Quick entry for '..plain(c and c.name or'this character')..' — Enter to add')
    f.capture:ClearAllPoints();f.capture:SetPoint('TOPLEFT',compact and 20 or 202,compact and -42 or -140);f.capture:SetWidth(compact and width-106 or bodyWidth-166)
    f.captureHint:SetWidth(f.capture:GetWidth()-16);f.captureHint:SetShown(f.capture:GetText()=='')
    f.add:ClearAllPoints();f.add:SetPoint('TOPRIGHT',compact and -12 or -104,compact and -42 or -140)
    f.details:SetShown(not compact);f.details:ClearAllPoints();f.details:SetPoint('TOPRIGHT',-28,-140)
    f.group:SetShown(tasks);f.group:ClearAllPoints();f.group:SetPoint('TOPLEFT',left,compact and -77 or -238);f.group:SetText(s.byActivity and'By activity'or'By character')
    f.view:ClearAllPoints();f.view:SetPoint('TOPLEFT',134,-77);f.view:SetText(W.manage and'Today'or'All tasks')
    f.prefs:SetShown(page=='preferences'and not compact);f.prefs:ClearAllPoints();f.prefs:SetPoint('TOPLEFT',194,-175);f.prefs:SetSize(bodyWidth,264);f.palette:SetText('Palette: '..theme().name)
    local rows
    if tasks then
        rows={};for _,r in ipairs(M.Rows(W.db,W.Now(),W.Resets(),W.manage))do
            if matches(r.task.text..' '..(r.task.category or'')..' '..W.ScopeText(r.task)..' '..rowName(r),query)then rows[#rows+1]=r end
        end
        table.sort(rows,function(a,b)
            local ka=s.byActivity and a.task.text or rowName(a);local kb=s.byActivity and b.task.text or rowName(b)
            if ka~=kb then return ka<kb end;if a.task.id~=b.task.id then return a.task.id<b.task.id end;return a.key<b.key
        end)
    elseif page=='preferences'then rows={}
    else rows=W.DirectoryRows(page,query)end
    W.visibleRows=rows
    local recorded=0;for _ in pairs(W.db.characters)do recorded=recorded+1 end
    local top=compact and 134 or(tasks and 278 or 204);local height=compact and 29 or 52;local gap=compact and 3 or 6
    W.pageSize=compact and(not s.compactSize and 12 or math.max(1,math.min(12,math.floor((f:GetHeight()-172)/32))))or math.max(1,math.min(12,math.floor((f:GetHeight()-top-48)/(height+gap))))
    local pages=math.max(1,math.ceil(#rows/W.pageSize));W.page=math.max(1,math.min(W.page or 1,pages))
    local visible=math.min(W.pageSize,math.max(0,#rows-(W.page-1)*W.pageSize))
    for i,card in ipairs(f.summary)do
        card:SetShown(not compact and tasks);card:ClearAllPoints();card:SetPoint('TOPLEFT',194+(i-1)*((bodyWidth-16)/3+8),-175);card:SetSize((bodyWidth-16)/3,51)
        card.heading:SetWidth((bodyWidth-16)/3-20);card.value:SetWidth((bodyWidth-16)/3-20)
    end
    local todayRows=M.Rows(W.db,W.Now(),W.Resets());local owners={};local shared=0;local archived=0
    for _,r in ipairs(todayRows)do if r.key=='@account'then shared=shared+1 else owners[r.key]=true end end
    local ownerCount=0;for _ in pairs(owners)do ownerCount=ownerCount+1 end
    for _,task in pairs(W.db.tasks)do if task.archived then archived=archived+1 end end
    f.summary[1].heading:SetText(W.manage and'SAVED TASKS'or'REMAINING');f.summary[1].value:SetText(tostring(W.manage and#M.Rows(W.db,W.Now(),W.Resets(),true)or#todayRows))
    f.summary[2].heading:SetText(W.manage and'RECORDED CHARACTERS'or'CHARACTERS WITH TASKS');f.summary[2].value:SetText(tostring(W.manage and recorded or ownerCount))
    f.summary[3].heading:SetText(W.manage and'ARCHIVED'or'SHARED TASKS');f.summary[3].value:SetText(tostring(W.manage and archived or shared))
    f.status:ClearAllPoints();f.status:SetPoint('TOPLEFT',compact and 12 or(tasks and 322 or 194),compact and -110 or(tasks and -243 or -179));f.status:SetWidth(compact and width-24 or bodyWidth-128)
    f.status:SetShown(page~='preferences');f.status:SetText(#rows..(page=='characters'and' recorded characters'or page=='categories'and' categories'or W.manage and' saved tasks'or' remaining')..(query~=''and' matching search'or''))
    if tasks then
    for i,row in ipairs(f.rows)do
        local r=i<=W.pageSize and rows[(W.page-1)*W.pageSize+i]or nil;row:SetShown(r~=nil)
        if r then
            row:ClearAllPoints();row:SetPoint('TOPLEFT',left,-top-(i-1)*(height+gap));row:SetSize(bodyWidth,height)
            row.title:SetWidth(bodyWidth-116);row.detail:SetWidth(bodyWidth-116);row.title:SetFontObject(compact and'GameFontHighlightSmall'or'GameFontHighlight');row.more:Show();row.done:Show();row.done:SetWidth(64)
            row.title:SetText(plain(r.task.text)..(r.task.archived and ' [Archived]'or'')..(compact and (' | '..plain(W.manage and W.ScopeText(r.task) or rowName(r))) or ''))
            row.detail:SetShown(not compact)
            row.detail:SetText(plain(W.manage and W.ScopeText(r.task) or rowName(r))..' | '..cadence[r.task.repeatMode]..(r.task.category~='' and (' | '..plain(r.task.category)) or ''))
            row.done:ClearAllPoints();row.done:SetPoint('TOPRIGHT',-38,-3);row.more:ClearAllPoints();row.more:SetPoint('TOPRIGHT',-5,-3)
            row.done:SetText(W.manage and (r.task.archived and 'Restore' or 'Edit') or (r.occurrence.waiting and '?' or 'Done'))
            row.done:SetScript('OnClick',function()
                if W.manage then
                    if r.task.archived then r.task.archived=false;W.Render()else W.EditTask(r.task)end
                elseif r.occurrence.waiting then W.Print('Regional reset data is unavailable; this task is waiting. No reset time is guessed.')
                else W.Action(r,'done')end
            end)
            row.more:SetScript('OnClick',function()
                local choices=W.manage and {{id='edit',name='Edit task'},{id='archive',name=r.task.archived and 'Restore task' or 'Archive task'}} or {{id='worked',name='Worked on it (keep unfinished)'},{id='postpone',name='Postpone until tomorrow'},{id='skip',name='Skip this occurrence'},{id='edit',name='Edit task'}}
                W.Choose('Task actions',choices,function(action)
                    if action=='edit' then W.EditTask(r.task)
                    elseif action=='archive' then r.task.archived=not r.task.archived;W.db.undo=nil;W.Render()
                    else W.Action(r,action)end
                end)
            end)
            row:SetScript('OnEnter',function(self)
                GameTooltip:SetOwner(self,'ANCHOR_RIGHT');GameTooltip:SetText(plain(r.task.text))
                GameTooltip:AddLine(plain(W.ScopeText(r.task)),1,1,1,true)
                GameTooltip:AddLine(r.task.progress=='account' and 'Shared completion: once for the account' or 'Separate completion for each eligible character',1,1,1,true)
                if r.occurrence and r.occurrence.waiting then GameTooltip:AddLine('Reset data unavailable',1,.7,.4,true)end
                if r.state and r.state.lastWorked then GameTooltip:AddLine('Last worked on: '..date('%b %d, %I:%M %p',r.state.lastWorked),1,1,1,true)end
                local character=W.db.characters[r.key]
                if character and character.lastSeen then GameTooltip:AddLine('Character last recorded: '..date('%b %d, %I:%M %p',character.lastSeen),.7,.7,.8,true)end
                GameTooltip:AddLine('Offline character details are recorded snapshots. Done is a manual check-in.',.7,.7,.8,true);GameTooltip:Show()
            end)
            row:SetScript('OnLeave',function()GameTooltip:Hide()end)
        end
    end
    else
        for i,row in ipairs(f.rows)do
            local r=i<=W.pageSize and rows[(W.page-1)*W.pageSize+i]or nil;row:SetShown(r~=nil)
            if r then
                row:ClearAllPoints();row:SetPoint('TOPLEFT',left,-top-(i-1)*(height+gap));row:SetSize(bodyWidth,height);row.title:SetWidth(bodyWidth-106);row.detail:SetWidth(bodyWidth-106)
                row.title:SetFontObject('GameFontHighlight');row.title:SetText(plain(r.title));row.detail:SetShown(true);row.detail:SetText(plain(r.detail));row.more:Hide()
                row.done:Show();row.done:ClearAllPoints();row.done:SetPoint('TOPRIGHT',-12,-13);row.done:SetWidth(78);row.done:SetText(page=='characters'and'Groups'or'Days')
                row.done:SetScript('OnClick',function()if page=='characters'then W.ManageCharacter(r.id)else W.CategoryEditor(r.id)end end)
                row:SetScript('OnEnter',function(self)
                    GameTooltip:SetOwner(self,'ANCHOR_RIGHT');GameTooltip:SetText(plain(r.title));GameTooltip:AddLine(plain(r.detail),1,1,1,true)
                    if r.character then GameTooltip:AddLine('Last recorded: '..(r.character.lastSeen and date('%b %d, %I:%M %p',r.character.lastSeen)or'Unknown'),1,1,1,true)end
                    GameTooltip:Show()
                end);row:SetScript('OnLeave',function()GameTooltip:Hide()end)
            end
        end
    end
    f.empty:SetShown(visible==0 and page~='preferences');f.empty:ClearAllPoints();f.empty:SetPoint('TOPLEFT',left+4,-top-8);f.empty:SetWidth(bodyWidth-8)
    f.empty:SetText(query~=''and'No matches. Clear the search to see the full list.'or tasks and'Nothing waiting here. Add one small next step above.'or'Log into your alts to record them, or refresh the character list in Preferences.')
    if compact and not s.compactSize and not W.resizing then W.layoutLock=true;f:SetHeight(top+math.max(visible*(height+gap),visible==0 and 60 or 0)+38);W.layoutLock=false end
    local bottom=f:GetHeight()-30
    f.pageLabel:ClearAllPoints();f.pageLabel:SetPoint('TOPLEFT',left,-bottom-6);f.pageLabel:SetWidth(bodyWidth-100);f.pageLabel:SetText('Page '..W.page..' / '..pages..' | v'..W.version)
    f.pageLabel:SetShown(page~='preferences');f.previous:SetShown(page~='preferences');f.next:SetShown(page~='preferences')
    f.previous:ClearAllPoints();f.previous:SetPoint('TOPRIGHT',-76,-bottom);f.next:ClearAllPoints();f.next:SetPoint('TOPRIGHT',-40,-bottom)
    f.previous:SetEnabled(W.page>1);f.next:SetEnabled(W.page<pages)
    W.ApplyTheme();W.rendering=false
end
