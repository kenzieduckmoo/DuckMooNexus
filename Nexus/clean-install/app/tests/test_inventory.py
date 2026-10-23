import unittest
from inventory_adapter import items


class InventoryTests(unittest.TestCase):
    def test_quality_and_locations_without_duplicate_legacy_bank(self):
        item={'itemID':123,'itemCount':3,'quality':4,'itemLink':'|Hitem:123|h[Ore |A:Professions-ChatIcon-Quality-12-Tier2:17:15::1|a]|h|r'}
        data={'SYNDICATOR_DATA':{'Version':2,'Characters':{'Test-Realm':{
            'bags':{1:{1:item}},'bank':{1:item},'bankTabs':{1:{'slots':{1:item}}},
            'containerInfo':{'bags':{1:item}}}}}}
        rows=list(items(data))
        self.assertEqual(len(rows),2)
        self.assertEqual({r['location'] for r in rows},{'bags','bankTabs'})
        self.assertTrue(all(r['crafting_quality']==2 and r['rarity']==4 and r['name']=='Ore' for r in rows))
        self.assertNotIn('observed_at',rows[0])

    def test_reject_unknown_schema_and_keep_missing_quality_unknown(self):
        with self.assertRaises(ValueError):list(items({'SYNDICATOR_DATA':{'Version':99}}))
        rows=list(items({'SYNDICATOR_DATA':{'Version':2,'Warband':{1:{'bank':{1:{'slots':{1:{'itemID':1,'itemCount':2,'quality':3}}}}}}}}))
        self.assertIsNone(rows[0]['crafting_quality'])


if __name__=='__main__':unittest.main()
