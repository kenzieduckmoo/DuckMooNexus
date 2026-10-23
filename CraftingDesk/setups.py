"""Small, versioned local store for user-entered crafting scenarios."""
import math

def validate_setups(value):
    if not isinstance(value, dict) or value.get('version') != 1 or not isinstance(value.get('setups'), list):
        raise ValueError('Unsupported saved setup format')
    if len(value['setups']) > 200: raise ValueError('Keep at most 200 saved setups')
    ids = set()
    for setup in value['setups']:
        if not isinstance(setup, dict): raise ValueError('Invalid setup')
        for key in ('id','name','recipeKey','scope','crafterName','realm','output','savedAt','materialSignature'):
            if not isinstance(setup.get(key), str) or not 1 <= len(setup[key]) <= 20000:
                raise ValueError('Missing or invalid setup field: '+key)
        if setup['id'] in ids: raise ValueError('Duplicate setup ID')
        ids.add(setup['id'])
        for key, low, high in (('count',1,10000),('fee',0,99.99),('concentration',0,100000),('quantity',1,100000)):
            number = setup.get(key)
            if isinstance(number,bool) or not isinstance(number,(int,float)) or not math.isfinite(number) or not low <= number <= high:
                raise ValueError('Invalid number: '+key)
        if int(setup['count']) != setup['count']: raise ValueError('Craft count must be a whole number')
        price=setup.get('salePrice')
        if price is not None and (isinstance(price,bool) or not isinstance(price,(int,float)) or not math.isfinite(price) or price<0):
            raise ValueError('Invalid sale price')
        if not isinstance(setup.get('selections'),dict) or not all(isinstance(k,str) and isinstance(v,str) for k,v in setup['selections'].items()):
            raise ValueError('Invalid reagent selections')
    return value

def validate_plan(value):
    validate_setups(value)
    completed=value.get('completed',[])
    validate_setups({'version':1,'setups':completed})
    for row in completed:
        at=row.get('completedAt')
        if isinstance(at,bool) or not isinstance(at,(int,float)) or not math.isfinite(at) or at<=0:
            raise ValueError('Invalid completion time')
    return {**value,'completed':completed}
