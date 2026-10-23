import gzip
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from urllib.error import HTTPError
import zipfile

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from savedvariables import read_lua
from financials import accountant,syndicator,canonical
from snapshots import capture
from source_importer import verify_archive
from bundle import create_bundle,unpack_bundle
from market_adapter import auctionator_rows
from api_collect import collect,endpoint


class SourcesTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def lua(self,raw):
        path=self.root/'Syndicator.lua';path.write_bytes(raw);return read_lua(path)
    def test_data_parser_rejects_code(self):
        for raw in (b'A = os.execute("bad")\n',b'A = {\n["x"] = function()\n}\n',b'while true do end\n',b'A = {\n'):
            with self.assertRaises(ValueError):self.lua(raw)
    def test_data_parser_rejects_duplicates(self):
        with self.assertRaises(ValueError):self.lua(b'A = {\n["a"] = 1,\n["a"] = 2,\n}\n')
    def test_binary_strings_preserved(self):
        p=self.root/'Auctionator.lua';p.write_bytes(b'A = {\n["x"] = "\\000\\255\\195\\169",\n}\n')
        self.assertEqual(read_lua(p,binary=True)[b'A'][b'x'],b'\x00\xff\xc3\xa9')
    def test_archive_and_bundle_roundtrip(self):
        p=self.root/'Syndicator.lua';raw=b'A = {\n["a"] = 123,\n}\n';p.write_bytes(raw)
        archive=self.root/'archive';meta=capture(p,archive,'retail-main-account')
        self.assertEqual(gzip.decompress((archive/meta['archive']).read_bytes()),raw)
        verify_archive(archive/meta['archive'],meta)
        mf=next(archive.glob('*.json'));packet=self.root/'p.bundle';create_bundle(mf,packet)
        dest=self.root/'unpacked';dest.mkdir();_,result=unpack_bundle(packet,dest)
        verify_archive(dest/result['archive'],result)
        bad={**meta,'raw_bytes':len(raw)+1}
        with self.assertRaises(ValueError):verify_archive(archive/meta['archive'],bad)
    def test_bundle_rejects_paths(self):
        p=self.root/'bad.bundle'
        with zipfile.ZipFile(p,'w') as z:z.writestr('../payload','bad')
        with self.assertRaises(ValueError):unpack_bundle(p,self.root)
    def test_bundle_rebuild_hash_is_independent_of_zip_clock(self):
        from unittest.mock import patch
        p=self.root/'Syndicator.lua';p.write_bytes(b'A = {\n}\n')
        capture(p,self.root/'archive','retail-main-account')
        mf=next((self.root/'archive').glob('*.json'))
        with patch('zipfile.time.localtime',return_value=(2026,10,20,1,2,4,0,0,0)):
            first=create_bundle(mf,self.root/'one.bundle')
        with patch('zipfile.time.localtime',return_value=(2026,10,21,3,4,6,0,0,0)):
            second=create_bundle(mf,self.root/'two.bundle')
        self.assertEqual(first,second)
        self.assertEqual((self.root/'one.bundle').read_bytes(),(self.root/'two.bundle').read_bytes())
    def test_ledger_idempotent_across_prepend(self):
        a=dict(timestamp=100,amount=10,balanceAfter=1000,type='DEPOSIT')
        b=dict(timestamp=200,amount=20,balanceAfter=980,type='WITHDRAW')
        def rows(entries):return list(accountant({'WarbandAccountantDB':{'ledger':dict(enumerate(entries,1))}}))
        old=rows([a]);new=rows([b,a]);self.assertEqual(old[0],new[1])
        duplicates=rows([a,a]);self.assertNotEqual(duplicates[0]['source_key'],duplicates[1]['source_key'])
    def test_combined_wealth_not_bank(self):
        d={'WarbandAccountantDB':{'ledger':{},'accountTotalHistory':{1:{'timestamp':1,'value':999}}}}
        self.assertEqual(list(accountant(d)),[])
    def test_unknown_source_time_not_replaced(self):
        r=list(syndicator({'SYNDICATOR_DATA':{'Warband':{1:{'money':100}}}}))[0]
        self.assertIsNone(r['observed_at']);self.assertEqual(r['precision'],'unknown')
    def test_auctionator_extrema_and_empty_cbor_maps(self):
        row={'h':{'10':120},'l':[],'a':{'10':5},'m':110}
        # Replace only the trusted codec boundary, preserving adapter logic.
        from unittest.mock import patch
        with patch('market_adapter.decode_cbor',return_value={'version':2,'i:1:variant':row}):
            rows=list(auctionator_rows({b'AUCTIONATOR_PRICE_DATABASE':{b'__dbversion':8,b'Realm':b'x'}}))
        self.assertEqual(rows[0][1],'i:1:variant')
        self.assertEqual(rows[0][5],{'lowest_low':120,'highest_low':120,'highest_quantity':5})
        self.assertIsNone(rows[1][2])
    def test_api_scope_validation(self):
        self.assertIn('auctions/commodities',endpoint('us',None))
        self.assertIn('connected-realm/1/auctions',endpoint('us',1))
        with self.assertRaises(ValueError):endpoint('attacker.example',1)
    def test_api_200_preserves_refresh_timestamp_and_raw(self):
        raw=b'{"auctions":[]}'
        class Response(io.BytesIO):
            status=200
            headers={'Last-Modified':'Tue, 20 Oct 2026 07:00:00 GMT','ETag':'"a"'}
        result=collect('us',None,self.root,'secret',opener=lambda *a,**k:Response(raw))
        self.assertEqual(result['source_modified_at'],'2026-10-20T07:00:00+00:00')
        self.assertNotEqual(result['source_modified_at'],result['fetched_at'])
        self.assertEqual(gzip.decompress((self.root/(result['sha256']+'.json.gz')).read_bytes()),raw)
        self.assertNotIn('secret',json.dumps(result))
    def test_api_304_and_rate_limit(self):
        for status in (304,429):
            def fail(*a,**k):raise HTTPError('https://us.api.blizzard.com',status,'test',{'Retry-After':'60'},None)
            r=collect('us',None,self.root,'secret',{'etag':'x','sha256':'a'},opener=fail)
            self.assertEqual(r['status'],status)
            self.assertNotIn('source_modified_at',r)


if __name__=='__main__':unittest.main()
