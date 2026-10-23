import unittest
from pathlib import Path
from unittest.mock import patch
from materials import market_data, item_tiers
from auctionator import decode_cbor, auctionator_prices
from importer import read_lua

class MarketTests(unittest.TestCase):
    def test_item_quality_ranks(self):
        cache={'versionStr':'19,enUS,build','itemStrings':{1:'i:1\x02i:2'},'data':'_'*23+'B'+'_'*23+'C'}
        self.assertEqual(item_tiers(cache),{'i:1':1,'i:2':2})
        cache['data']='_'*23+'L'+'_'*23+'M'
        self.assertEqual(item_tiers(cache),{'i:1':1,'i:2':2})
        cache['versionStr']='20,enUS,build'
        self.assertEqual(item_tiers(cache),{})
        cache['versionStr']='19,enUS,build';cache['data']='short'
        with self.assertRaises(ValueError):item_tiers(cache)
    def test_tsm_sales_scale_and_region(self):
        with patch.object(Path,'read_text',return_value='LoadData("AUCTIONDB_REGION_SALE","US",[[return {downloadTime=123,fields={"itemString","regionSale","regionSoldPerDay","regionSalePercent"},data={{42,10,1V8,4M}}}]])'):
            record=market_data(Path('fixture'))['sales']['i:42']
            self.assertEqual(record['saleRate'],.15)
            self.assertEqual(record['dailySold'],2.024)

    def test_binary_lua_and_cbor(self):
        with patch.object(Path,'read_bytes',return_value=b'DB = "\\161A1\\161Am\\026\\000\\001\\000\\000"\n'):
            raw=read_lua(Path('fixture'),True)['DB']
            self.assertEqual(decode_cbor(raw),{'1':{'m':65536}})
        for raw in (b'\xa1',b'\x00\x00',b'\x9f'):
            with self.assertRaises(ValueError):decode_cbor(raw)

    def test_prices_keep_scope_and_skip_variants(self):
        row={'m':123,'h':{'2478':123}}
        db={'__dbversion':8,'One':{'42':row,'43':row,'g:43:100':row},'Broken':'\x01\x0a'}
        data=auctionator_prices(db,{'commodities':{'i:42':{}}})
        self.assertEqual(data['commodities']['i:42']['price'],123)
        self.assertIn('i:43',data['realms']['one'])
        self.assertEqual(data['entries'],2)
        self.assertEqual(len(data['warnings']),1)
        self.assertIn('No readable saved price table for Broken',data['warnings'][0])
        self.assertTrue(data['commodities']['i:42']['dayPrecision'])

    def test_non_table_realm_does_not_discard_other_prices(self):
        data=auctionator_prices({'__dbversion':8,'Broken':'\x01','Good':{'42':{'m':99,'h':{'2478':99}}}}, {})
        self.assertEqual(data['realms']['good']['i:42']['price'],99)
        self.assertEqual(len(data['warnings']),1)

if __name__=='__main__':unittest.main()
