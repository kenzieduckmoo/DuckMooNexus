"""Friendly labels over stable database field names."""


def format_table(obj):
    if obj.get('type')!='table':return
    obj['fieldConfig']['defaults']['noValue']='—'
    names={'name':'Item','item':'Item','crafting_quality':'Crafting rank','crafting_rank':'Crafting rank',
        'owner_kind':'Owner type','owner':'Character / bank','owner_key':'Character / bank','location':'Location',
        'quantity':'Quantity','is_bound':'Binding','rarity':'Rarity','item_id':'Item ID',
        'snapshot_file_saved_at':'Cache file saved','lowest_unit_gold':'Lowest unit price',
        'invoice_g':'Invoice gold','item_variant':'Variant details','source_modified_at':'Market updated',
        'fetched_at':'Fetched','scope':'Market','listings':'Listings','characters':'Characters',
        'guilds':'Guild caches','warbanks':'Warbanks','stacks':'Item stacks','file_saved_at':'Cache file saved'}
    maps={'location':{'bags':'Bags','bank':'Bank','bankTabs':'Character bank','equipped':'Equipped',
          'mail':'Mail','auctions':'Posted auctions','void':'Void storage'},
        'owner_kind':{'character':'Character','warband':'Warband','guild':'Guild'},
        'is_bound':{'true':'Bound','false':'Unbound'},
        'rarity':{'0':'Poor','1':'Common','2':'Uncommon','3':'Rare','4':'Epic','5':'Legendary','6':'Artifact','7':'Heirloom'},
        'scope':{'commodities':'US commodities',**{'connected-realm:'+key:label for key,label in {
            '11':'Tichondrius','57':'Illidan','61':"Zul'jin",'63':'Ysera','76':'Sargeras','99':'Llane',
            '104':'Garona / Malygos','162':'Emerald Dream','1426':'Aerie Peak','3675':'Moon Guard',
            '3685':'Turalyon','3721':'Saurfang','3726':"Aman'Thul / Khaz'goroth"}.items()}}}
    overrides=obj['fieldConfig'].setdefault('overrides',[])
    for field,label in names.items():
        properties=[{'id':'displayName','value':label}]
        widths={'name':300,'item':300,'owner':250,'owner_key':250,'crafting_quality':110,'crafting_rank':110,
            'owner_kind':110,'location':160,'quantity':95,'is_bound':95,'rarity':110,'item_id':85,'lowest_unit_gold':155}
        if field in widths:properties.append({'id':'custom.width','value':widths[field]})
        if field in maps:
            properties.append({'id':'mappings','value':[{'type':'value','options':{
                key:{'text':text} for key,text in maps[field].items()}}]})
        if field in ('lowest_unit_gold','invoice_g'):
            properties.extend([{'id':'unit','value':'suffix:g'},{'id':'decimals','value':4}])
        overrides[:]=[o for o in overrides if o.get('matcher')!={'id':'byName','options':field}]
        overrides.append({'matcher':{'id':'byName','options':field},'properties':properties})
