import unittest
from captures import acquisition_offers

class AcquisitionTests(unittest.TestCase):
    def test_import_preserves_payment_and_character(self):
        db={'characters':{'one':{'name':'Test','realm':'Realm','acquisitionOffers':{
            'offer':{'kind':'vendor','observedAt':100,'itemID':123,'price':0,'canAfford':False,
                     'costs':{1:{'amount':20,'name':'Currency'}},'tooltip':{1:'Requires Renown 10'}}}}}}
        row=acquisition_offers(db)[0]
        self.assertEqual(row['guid'],'one')
        self.assertFalse(row['canAfford'])
        self.assertEqual(row['costs'],[{'amount':20,'name':'Currency'}])
        self.assertEqual(row['tooltip'],['Requires Renown 10'])
        self.assertNotIn('recipeID',row)
    def test_missing_old_or_invalid_records(self):
        self.assertEqual(acquisition_offers({'characters':{'one':{}}}),[])
        self.assertEqual(acquisition_offers({'characters':{'one':{'acquisitionOffers':{'bad':{'kind':'vendor','observedAt':False}}}}}),[])
