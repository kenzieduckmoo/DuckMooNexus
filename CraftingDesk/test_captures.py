import unittest
from copy import deepcopy
from captures import captured_recipes, capture_catalog, with_scanned_operations, scan_coverage

class CapturesTests(unittest.TestCase):
    def fixture(self):
        record={'recipeID':123,'output':{'itemID':101,'hyperlink':'|Hitem:101|h[Result]|h'},'quantity':2,'name':'Recipe',
                'schematic':{'quantityMin':2,'quantityMax':2,'reagentSlotSchematics':{1:{'dataSlotType':1,'dataSlotIndex':1,'required':True,'quantityRequired':3}}},
                'observedAt':1000,'applyConcentration':True,'allocations':{1:{'dataSlotType':1,'dataSlotIndex':1,'reagent':{'itemID':11},'quantity':1},2:{'dataSlotType':1,'dataSlotIndex':1,'reagent':{'itemID':12},'quantity':2}},
                'operation':{'concentrationCost':100,'craftingQuality':2},'skillLineID':2906}
        return {'schemaVersion':1,'characters':{'Player-test':{'name':'Tester','realm':'TestRealm','faction':'Alliance','operations':{'capture':record}}}}

    def test_mixed_qualities_and_identity(self):
        db=self.fixture(); recipes,names,skipped=captured_recipes(db,{'commodities':{'i:101':{}}})
        self.assertEqual(skipped,0)
        self.assertEqual(recipes[0]['materials'],{'i:11':1,'i:12':2})
        self.assertEqual(recipes[0]['crafters'][0]['guid'],'Player-test')
        self.assertEqual(names['i:101'],'Result')
        self.assertFalse(recipes[0]['capture']['manualSalePrice'])
        self.assertTrue(captured_recipes(db,{})[0][0]['capture']['manualSalePrice'])

    def test_bad_data_skipped(self):
        db=self.fixture(); r=db['characters']['Player-test']['operations']['capture']
        r['allocations'][2]['quantity']=1
        self.assertEqual(captured_recipes(db,{})[2],1)
        r['allocations'][2]['quantity']=2;r['operation']['concentrationCost']=None
        self.assertEqual(captured_recipes(db,{})[2],1)
        r['applyConcentration']=False
        self.assertEqual(captured_recipes(db,{})[0][0]['capture']['concentration'],0)

    def test_catalog_without_operation(self):
        db=self.fixture(); character=db['characters']['Player-test']; character['operations']={}
        character['recipes']={123:{'info':{'name':'Unknown recipe','learned':False,'firstCraft':False},'observedAt':1000}}
        catalog=capture_catalog(db)
        self.assertEqual(len(catalog),1)
        self.assertFalse(catalog[0]['learned'])
        self.assertIs(catalog[0]['firstCraft'],False)
        self.assertIsNone(catalog[0]['schematic'])
        self.assertEqual(captured_recipes(db,{})[0],[])

    def test_zero_cost_duplicate_is_not_an_import_error(self):
        db=self.fixture(); ops=db['characters']['Player-test']['operations']
        ops['capture']['operation']['concentrationCost']=0
        # An unmatched zero-cost preview must not become a free craft.
        self.assertEqual(captured_recipes(db,{})[2],1)
        ops['normal']=deepcopy(ops['capture']);ops['normal']['applyConcentration']=False
        recipes,_,skipped=captured_recipes(db,{})
        self.assertEqual(len(recipes),1);self.assertEqual(skipped,0)
        self.assertFalse(recipes[0]['capture']['applyConcentration'])
        ops['normal']['operation']['craftingQuality']=1
        self.assertEqual(captured_recipes(db,{})[2],1)
        ops['normal']['operation']['craftingQuality']=2
        ops['normal']['observedAt']=None
        self.assertEqual(captured_recipes(db,{})[2],2)

    def test_compact_scan_import(self):
        db=self.fixture();c=db['characters']['Player-test'];r=c['operations'].pop('capture')
        c['scannedRecipes']={123:{'info':{'recipeID':123,'name':'Scanned'},'schematic':r['schematic'],
            'profession':{'professionID':2906},'limited':True,'outcomes':{'mixed':r}}}
        c['scanStatus']={2906:{'state':'Paused','checked':1,'total':2}}
        expanded=with_scanned_operations(db)
        recipes,_,skipped=captured_recipes(expanded,{})
        self.assertEqual(skipped,0);self.assertEqual(recipes[0]['capture']['source'],'recipe-scan')
        self.assertTrue(recipes[0]['capture']['scanLimited'])
        self.assertEqual(recipes[0]['materials'],{'i:11':1,'i:12':2})
        self.assertEqual(c['operations'],{})
        self.assertEqual(scan_coverage(db)[0]['state'],'Paused')
        c['scanStatus'][0]={'state':'Paused','checked':0}
        self.assertEqual(len(scan_coverage(db)),1)

if __name__=='__main__': unittest.main()
