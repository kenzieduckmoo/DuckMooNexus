"""Preserve catalog, scan definitions/outcomes and selected operations separately.

Matches Crafting Desk captures.py's schema, without expanding each outcome to
duplicate the recipe schematic. These are observations, not completed crafts.
"""
def crafting_rows(data):
    db = data['DuckMooCaptureDB']
    if db.get('schemaVersion') != 1:
        raise ValueError('Unsupported Capture schema')
    for guid, character in db.get('characters', {}).items():
        identity = {k: character.get(k) for k in ('name','realm','faction','build')}
        yield guid, None, 'character', guid, None, identity
        for profession_id, status in character.get('scanStatus', {}).items():
            yield guid,None,'scan_status',str(profession_id),status.get('observedAt'),status
        if character.get('captureStatus'):
            status=character['captureStatus']
            yield guid,None,'capture_status','status',status.get('observedAt'),status
        for recipe_id, record in character.get('recipes', {}).items():
            yield guid, int(recipe_id), 'catalog', str(recipe_id), record.get('observedAt'), record
        for recipe_id, scan in character.get('scannedRecipes', {}).items():
            yield guid, int(recipe_id), 'scan_definition', str(recipe_id), scan.get('observedAt'), {k:v for k,v in scan.items() if k!='outcomes'}
            for key, outcome in scan.get('outcomes', {}).items():
                yield guid, int(recipe_id), 'scan_outcome', str(key), outcome.get('observedAt'), outcome
        for key, record in character.get('operations', {}).items():
            yield guid, record.get('recipeID'), 'selected_operation', str(key), record.get('observedAt'), record
        for key, offer in character.get('acquisitionOffers', {}).items():
            yield guid, None, 'acquisition_offer', str(key), offer.get('observedAt'), offer
