"""Validate personal guide choices/progress independently of crafting plans."""
import re
def validate_guides(value):
    if not isinstance(value,dict) or value.get('version')!=1 or not isinstance(value.get('profiles'),dict) or len(value['profiles'])>500:raise ValueError('Invalid guide progress')
    out={'version':1,'profiles':{}}
    for key,profile in value['profiles'].items():
        if not isinstance(key,str) or not re.fullmatch(r'Player-\d+-[A-Fa-f0-9]+\|(Alchemy|Blacksmithing|Enchanting|Engineering|Inscription|Jewelcrafting|Leatherworking|Tailoring)',key) or not isinstance(profile,dict):raise ValueError('Invalid guide character/profession')
        clean={'choices':{},'done':{}}
        for field in ('lining','gear'):
            if field in profile:
                if not isinstance(profile[field],str) or len(profile[field])>250:raise ValueError('Invalid recipe selection')
                clean[field]=profile[field]
        for field in ('choices','done'):
            data=profile.get(field,{})
            if not isinstance(data,dict) or len(data)>500:raise ValueError('Too many guide entries')
            for k,v in data.items():
                if not isinstance(k,str) or len(k)>350:raise ValueError('Invalid guide step')
                if field=='choices' and (not re.fullmatch(r'\d{1,3}',k) or not isinstance(v,str) or len(v)>250):raise ValueError('Invalid route choice')
                if field=='done' and type(v) is not bool:raise ValueError('Invalid guide checkmark')
                clean[field][k]=v
        out['profiles'][key]=clean
    return out
