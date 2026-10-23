import unittest
from datetime import datetime,timezone
from api_worker import retry_seconds


class RetryTests(unittest.TestCase):
    def test_retry_after_numeric_and_http_date(self):
        at=datetime(2026,10,23,tzinfo=timezone.utc)
        self.assertEqual(retry_seconds('1800',at),1800)
        self.assertEqual(retry_seconds('Fri, 23 Oct 2026 00:30:00 GMT',at),1800)
        self.assertEqual(retry_seconds(None,at),900)
        self.assertEqual(retry_seconds('-1',at),60)


if __name__=='__main__':unittest.main()
