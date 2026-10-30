import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from api_collect import unique_auctions
from api_worker import replay_pending


class DuplicateAuctionTests(unittest.TestCase):
    def test_identical_listings_count_once_but_distinct_ids_remain(self):
        a = {'id': 1, 'item': {'id': 244623}, 'quantity': 1, 'buyout': 14718900}
        b = {**a, 'id': 2}
        rows = [a, dict(a), b]
        self.assertEqual(unique_auctions(rows), [a, b])
        self.assertEqual(len(rows), 3)
        with self.assertRaisesRegex(ValueError, 'Conflicting'):
            unique_auctions([a, {**a, 'buyout': 1}])

    def test_bad_pending_response_does_not_block_next_response(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp)
            for name in ('a', 'b'):
                (archive / ('pending-'+name+'.json')).write_text(json.dumps({'scope': name}))
            with patch('api_worker.ingest_api', side_effect=[ValueError('bad data'), 42]) as ingest:
                replay_pending(None, archive)
            self.assertEqual(ingest.call_count, 2)
            self.assertTrue((archive/'rejected-a.json').exists())
            self.assertTrue((archive/'imported-b.json').exists())

    def test_transient_pending_failure_stays_queued(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp)
            pending = archive/'pending-a.json'
            pending.write_text('{}')
            with patch('api_worker.ingest_api', side_effect=ConnectionError('temporary')):
                replay_pending(None, archive)
            self.assertTrue(pending.exists())


if __name__ == '__main__':
    unittest.main()
