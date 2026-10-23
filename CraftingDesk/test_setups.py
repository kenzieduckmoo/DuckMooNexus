import unittest
from setups import validate_setups, validate_plan

class SetupValidationTests(unittest.TestCase):
    def fixture(self):
        setup={k:'example' for k in ('id','name','recipeKey','scope','crafterName','realm','output','savedAt','materialSignature')}
        setup.update(count=1,fee=5,concentration=100,quantity=2,salePrice=None,selections={'i:1':'i:1'})
        return {'version':1,'setups':[setup]}

    def test_valid_and_empty(self):
        validate_setups(self.fixture())
        validate_setups({'version':1,'setups':[]})

    def test_plan_completion_history(self):
        value=self.fixture()
        self.assertEqual(validate_plan(value)['completed'],[])
        value['completed']=[dict(value['setups'][0],completedAt=1234)]
        self.assertEqual(validate_plan(value)['completed'][0]['count'],1)
        for invalid in (None,True,-1,float('nan')):
            value['completed'][0]['completedAt']=invalid
            with self.assertRaises(ValueError):validate_plan(value)

    def test_invalid_numbers(self):
        for key,value in [('count',0),('count',1.5),('count',True),('fee',100),('concentration',-1),('salePrice',float('nan'))]:
            with self.subTest(key=key,value=value):
                data=self.fixture(); data['setups'][0][key]=value
                with self.assertRaises(ValueError): validate_setups(data)

    def test_bad_selections_and_duplicate(self):
        data=self.fixture(); data['setups'][0]['selections']={'i:1':{}}
        with self.assertRaises(ValueError): validate_setups(data)
        data=self.fixture(); data['setups']*=2
        with self.assertRaises(ValueError): validate_setups(data)

if __name__=='__main__': unittest.main()
