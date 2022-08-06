import unittest

import enum

from binaryparse import *

class TestBinaryParse(unittest.TestCase):
    def test_struct_parser(self):
        packed = b'AAAAB'

        c = struct_parser("<4s")

        s, result, rest = c(packed)

        self.assertTrue(s)
        self.assertEqual(result, b'AAAA')
        self.assertEqual(rest, b'B')

    def test_struct_parser_negative(self):
        bad_packed = b'AAA'

        c = struct_parser("<4s")

        s, result, rest = c(bad_packed)
        self.assertFalse(s)


    def test_str_parser_ascii(self):
        packed = b'AAAAB'

        c = str_parser(4)

        s, result, rest = c(packed)

        self.assertTrue(s)
        self.assertEqual(result, 'AAAA')
        self.assertEqual(rest, b'B')

    def test_str_parser_cp1252(self):
        packed = 'test'.encode('cp1252') + b'a'

        c = str_parser(4, 'cp1252')

        s, result, rest = c(packed)

        self.assertTrue(s)
        self.assertEqual(result, "test")
        self.assertEqual(rest, b'a')


    def test_record_parser(self):
        packed = b'AAAA\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00\x04\x00\x00\x00'

        record_type = struct_parser("<4s")
        unsigned_long = struct_parser("<L")

        header = record_parser("header", (
            ("type", record_type),
            ("size", unsigned_long),
            ("flags", unsigned_long),
            ("formid", unsigned_long),
            ("m", unsigned_long),
        ))

        s, result, rest = header(packed)

        self.assertTrue(s)
        self.assertEqual(rest, b'')
        self.assertEqual(result.type, b"AAAA")
        self.assertEqual(result.size, 1)
        self.assertEqual(result.flags, 2)
        self.assertEqual(result.formid, 3)
        self.assertEqual(result.m, 4)


    def test_zstr_parser_cp1252(self):
        packed = 'test'.encode('cp1252') + b'\0abc'

        c = zstr_parser('cp1252')

        s, result, rest = c(packed)

        self.assertTrue(s)
        self.assertEqual(rest, b'abc')
        self.assertEqual(result, 'test')


    def test_enum_parser(self):
        class TestEnum(enum.IntFlag):
            R = 4
            W = 2
            X = 1

        packed = b'\x05\x00\x00\x00\x01'

        c = enum_parser(struct_parser('<L'), TestEnum)

        s, result, rest = c(packed)

        self.assertTrue(s)
        self.assertEqual(rest, b'\x01')
        self.assertEqual(result, {TestEnum.X, TestEnum.R})


if __name__ == "__main__":
    unittest.main()
