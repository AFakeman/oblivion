import unittest

from oblivion_types import *


class TestOblivionParse(unittest.TestCase):
    def test_subrecord_parse_default(self):
        packed = b'EDID\x0b\x00ADMIRELIKE\x00QSTI'

        s, r, b = subrecord("FAKE", packed)

        self.assertTrue(s)
        self.assertEqual(b, b'QSTI')
        self.assertEqual(r.type, 'EDID')
        self.assertEqual(r.data, b'ADMIRELIKE\x00')

    def test_subrecord_parse_correct(self):
        packed = b'EDID\x0b\x00ADMIRELIKE\x00QSTI'

        s, r, b = subrecord("DIAL", packed)

        self.assertTrue(s)
        self.assertEqual(b, b'QSTI')
        self.assertEqual(r.type, 'EDID')
        self.assertEqual(r.data.editorId, 'ADMIRELIKE')

    def test_subrecord_parse_werid(self):
        packed = b'DATA\x02\x00\x01\x00QSTI'

        s, r, b = subrecord("DIAL", packed)

        self.assertTrue(s)
        self.assertEqual(r.type, 'DATA')
        self.assertEqual(b, b'QSTI')

    def test_record_parse(self):
        packed = b''\
            b'DIAL>\x00\x00\x00\x00\x00\x00\x00\xac\x00\x00\x00\x1c\x1f\x18\x00'\
            b'EDID\x0b\x00ADMIRELIKE\x00'\
            b'QSTI\x04\x00"\xe7\x01\x00'\
            b'QSTI\x04\x00\x02\x06\x01\x00'\
            b'FULL\x0c\x00ADMIRE_LIKE\x00'\
            b'DATA\x01\x00\x03END'

        s, r, b = record(packed)

        self.assertTrue(s)
        self.assertEqual(r.header.type, 'DIAL')
        self.assertEqual(r.subrecords[0].type, 'EDID')
        self.assertEqual(r.subrecords[0].data.editorId, 'ADMIRELIKE')
        self.assertEqual(r.subrecords[1].type, 'QSTI')
        self.assertEqual(r.subrecords[2].type, 'QSTI')
        self.assertEqual(r.subrecords[3].type, 'FULL')
        self.assertEqual(r.subrecords[4].type, 'DATA')
        self.assertEqual(b, b'END')

    def test_info_parse(self):
        packed = b""\
            b"INFOa\x00\x00\x00\x00\x00\x00\x00\xab\xb2\x18\x00\x1a\x1f\x1e\x00"\
            b"DATA\x03\x00\x03\x00\x02"\
            b"QSTI\x04\x00\x02\x06\x01\x00"\
            b"TRDT\x10\x00\x00\x00\x00\x002\x00\x00\x00\x00\x00\x00\x00\x01&A\x02"\
            b"NAM1\x11\x00You're too kind.\x00"\
            b"NAM2\x01\x00\x00"\
            b"SCHR\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        s, r, b = record(packed)

        self.assertTrue(s)
        self.assertEqual(r.header.type, 'INFO')
        self.assertEqual(r.subrecords[3].data.responseText, "You're too kind.")
        self.assertEqual(r.subrecords[4].data.actorNotes, "")

    def test_grup_parse(self):
        packed = b""\
            b"GRUP[\x02\x00\x00\xac\x00\x00\x00\x07\x00\x00\x00\x1a\x1f\x1e\x00"\
            b"INFOa\x00\x00\x00\x00\x00\x00\x00\xab\xb2\x18\x00\x1a\x1f\x1e\x00"\
            b"DATA\x03\x00\x03\x00\x02QSTI\x04\x00\x02\x06\x01\x00"\
            b"TRDT\x10\x00\x00\x00\x00\x002\x00\x00\x00\x00\x00\x00\x00\x01&A\x02"\
            b"NAM1\x11\x00You're too kind.\x00"\
            b"NAM2\x01\x00\x00"\
            b"SCHR\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"\
            b"INFOa\x00\x00\x00\x00\x00\x00\x00\xac\xb2\x18\x00\x1a\x1f\x1e\x00"\
            b"DATA\x03\x00\x03\x00\x02"\
            b"QSTI\x04\x00\x02\x06\x01\x00"\
            b"TRDT\x10\x00\x00\x00\x00\x002\x00\x00\x00\x00\x00\x00\x00\x01\x02@\x02"\
            b"NAM1\x11\x00I like you, too.\x00"\
            b"NAM2\x01\x00\x00"\
            b"SCHR\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"\
            b"INFO[\x00\x00\x00\x00\x00\x00\x00\xad\xb2\x18\x00\x1d\x1f\x1e\x00"\
            b"DATA\x03\x00\x03\x00\x02"\
            b"QSTI\x04\x00\x02\x06\x01\x00"\
            b"TRDT\x10\x00\x00\x00\x00\x002\x00\x00\x00\x00\x00\x00\x00\x01\x02@\x02"\
            b"NAM1\x0b\x00Thank you.\x00"\
            b"NAM2\x01\x00\x00"\
            b"SCHR\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"\
            b"INFOZ\x00\x00\x00\x00\x00\x00\x00\r#\x06\x00\x1d\x1f\x1e\x00"\
            b"DATA\x03\x00\x03\x00\x02"\
            b"QSTI\x04\x00\x02\x06\x01\x00"\
            b"TRDT\x10\x00\x00\x00\x00\x002\x00\x00\x00\x00\x00\x00\x00\x01\x02@\x02"\
            b"NAM1\n\x00How nice.\x00"\
            b"NAM2\x01\x00\x00"\
            b"SCHR\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"\
            b"INFOl\x00\x00\x00\x00\x00\x00\x00\x0e#\x06\x00\x1d\x1f\x1e\x00"\
            b"DATA\x03\x00\x03\x00\x02"\
            b"QSTI\x04\x00\x02\x06\x01\x00"\
            b"TRDT\x10\x00\x00\x00\x00\x002\x00\x00\x00\x00\x00\x00\x00\x01\x02@\x02"\
            b"NAM1\x1c\x00It's good of you to say so.\x00"\
            b"NAM2\x01\x00\x00"\
            b"SCHR\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00END"


        s, g, b = grup(packed)

        self.assertTrue(s)
        self.assertEqual(b, b'END')

    def test_record_parse_no_header(self):
        packed = b''\
            b'DIAL>\x00\x00\x00\x00\x00\x00\x00\xac\x00\x00\x00\x1c\x1f\x18\x00'\
            b'EDID\x0b\x00ADMIRELIKE\x00'\
            b'QSTI\x04\x00"\xe7\x01\x00'\
            b'QSTI\x04\x00\x02\x06\x01\x00'\
            b'FULL\x0c\x00ADMIRE_LIKE\x00'\
            b'DATA\x01\x00\x03END'

        s, h, r = record_header(packed)
        self.assertTrue(s)
        self.assertEqual(h.type, 'DIAL')

        s, r, b = record(r, header=h)

        self.assertTrue(s)
        self.assertEqual(r.header.type, 'DIAL')
        self.assertEqual(r.subrecords[0].type, 'EDID')
        self.assertEqual(r.subrecords[0].data.editorId, 'ADMIRELIKE')
        self.assertEqual(r.subrecords[1].type, 'QSTI')
        self.assertEqual(r.subrecords[2].type, 'QSTI')
        self.assertEqual(r.subrecords[3].type, 'FULL')
        self.assertEqual(r.subrecords[4].type, 'DATA')
        self.assertEqual(b, b'END')

if __name__ == "__main__":
    unittest.main()
