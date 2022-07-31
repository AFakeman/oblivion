import unittest

from binaryparse import *

class TestBinaryParse(unittest.TestCase):
    def test_typedef(self):
        parser = BinaryParser()
        parser.typedef("record_type", "4s")
        self.assertEqual(parser.format_for_type("record_type"), "4s")

    def test_register(self):
        parser = BinaryParser()

        self.assertRaises(ValueError, parser.format_for_type, "header")

        parser.typedef("record_type", "4s")
        parser.register("header", [
            ("record_type", "type"),
            ("unsigned long", "size"),
            ("unsigned long", "flags"),
            ("unsigned long", "formid"),
            ("unsigned long", "m"),
        ])

        self.assertEqual(parser.format_for_type("header"), "<4sLLLL")

    def test_fieldcount(self):
        parser = BinaryParser()

        self.assertRaises(ValueError, parser.field_count, "record")

        parser.typedef("record_type", "4s")
        parser.register("header", [
            ("record_type", "type"),
            ("unsigned long", "size"),
            ("unsigned long", "flags"),
            ("unsigned long", "formid"),
            ("unsigned long", "m"),
        ])

        parser.register("record_body", [
            ("char", "symbol"),
            ("unsigned long", "length"),
        ])
        parser.register("record", [
            ("header", "header"),
            ("record_body", "body"),
        ])
        self.assertEqual(parser.field_count("record"), 7)

    def test_sizeof(self):
        parser = BinaryParser()
        parser.typedef("record_type", "4s")
        parser.typedef("description_type", "256s")
        parser.typedef("name_type", "32s")

        parser.register("record", [
            ("record_type", "type"),
            ("description_type", "description"),
            ("name_type", "name"),
        ])

        self.assertEqual(parser.sizeof("record"), 4 + 256 + 32)

    def test_parse_from_tuple(self):
        parser = BinaryParser()

        parser.typedef("record_type", "4s")
        parser.register("header", [
            ("record_type", "type"),
            ("unsigned long", "size"),
            ("unsigned long", "flags"),
            ("unsigned long", "formid"),
            ("unsigned long", "m"),
        ])

        parser.register("record_body", [
            ("char", "symbol"),
            ("unsigned long", "length"),
        ])
        parser.register("record", [
            ("header", "header"),
            ("record_body", "body"),
        ])

        t = parser.parse_from_tuple("record", ("AAAA", 1, 2, 3, 4, "a", 5))

        self.assertEqual(t.header.type, "AAAA")
        self.assertEqual(t.header.size, 1)
        self.assertEqual(t.header.flags, 2)
        self.assertEqual(t.header.formid, 3)
        self.assertEqual(t.header.m, 4)

        self.assertEqual(t.body.symbol, "a")
        self.assertEqual(t.body.length, 5)

    def test_parse_from_binary(self):
        parser = BinaryParser()

        parser.typedef("record_type", "4s")
        parser.register("header", [
            ("record_type", "type"),
            ("unsigned long", "size"),
            ("unsigned long", "flags"),
            ("unsigned long", "formid"),
            ("unsigned long", "m"),
        ])

        packed = b'AAAA\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00\x04\x00\x00\x00'
        t = parser.parse_from_bytes("header", packed)

        self.assertEqual(t.type, b"AAAA")
        self.assertEqual(t.size, 1)
        self.assertEqual(t.flags, 2)
        self.assertEqual(t.formid, 3)
        self.assertEqual(t.m, 4)


if __name__ == "__main__":
    unittest.main()
