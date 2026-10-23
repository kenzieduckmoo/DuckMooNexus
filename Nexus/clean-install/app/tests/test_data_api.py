import unittest
from nexus_data_api import get_query


class DataApiTests(unittest.TestCase):
    def test_parameterized_names_and_bounded_results(self):
        sql,values=get_query('/api/v1/items',{'q':["ore' OR true --"],'limit':['99999']})
        self.assertNotIn("ore'",sql)
        self.assertIn("ore' OR true --",values)
        self.assertEqual(values[-1],500)
        with self.assertRaises(ValueError):get_query('/api/v1/market',{'item_id':['garbage']})
        with self.assertRaises(LookupError):get_query('/api/v1/raw-sql',{})
