import unittest

from sqlalchemy.exc import IntegrityError

from fangfrisch.db import RefreshLog
from fangfrisch.db import Session
from tests import FangfrischTest

ID1 = 'test_1'
ID2 = 'test_2'


class DbTests(FangfrischTest):
    s = None

    def setUp(self) -> None:
        super().setUp()
        self.s = Session()
        self.s.query(RefreshLog).delete()
        self.s.add(RefreshLog(ID1))
        self.s.commit()

    def test_duplicate(self):
        self.s.add(RefreshLog(ID1))
        with self.assertRaises(IntegrityError):
            self.s.commit()

    def test_insert(self):
        self.s.add(RefreshLog(ID2))
        self.s.commit()
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
