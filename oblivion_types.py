import enum

import binaryparse


class SubrecordCount(enum.Enum):
    REQUIRED='+'
    OPTIONAL='-'
    REPEATING='*'

class HeaderFlags(enum.IntFlag):
    ESM_RECORD = 0x00000001
    DELETED = 0x00000020
    CASTS_SHADOWS = 0x00000200
    PERS_REF = 0x00000400
    INIT_DISABLED = 0x00000800
    IGNORED = 0x00001000
    DIST_VIS = 0x00008000
    OFF_LIMITS = 0x00020000
    COMPRESSED = 0x00040000
    CANT_WAIT = 0x00080000

zstr = binaryparse.zstr_parser('cp1252')
record_type = binaryparse.str_parser(4)
grup_label = binaryparse.struct_parser('<4s')
unsigned_long = binaryparse.struct_parser("<L")
formid = unsigned_long
unsigned_short = binaryparse.struct_parser("<H")
byte = binaryparse.struct_parser("<b")

header_flags = binaryparse.enum_parser(unsigned_long, HeaderFlags)


def formid(bstr):
    s, r, rem = unsigned_long(bstr)
    if not s:
        return s, r, rem

    r = "{0:#0{1}x}".format(r,10)
    return s, r, rem


header = binaryparse.record_parser("header", (
    ("type", record_type),
    ("size", unsigned_long),
    ("flags", header_flags),
    ("formid", unsigned_long),
    ("m", unsigned_long),
))

grup_header = binaryparse.record_parser("grup_header", (
    ("type", record_type),
    ("size", unsigned_long),
    ("label", grup_label),
    ("group_type", unsigned_long),
    ("vcs_info", unsigned_long),
))

subrecord_header = binaryparse.record_parser("subrecord_header", (
    ("type", record_type),
    ("size", unsigned_short),
))


def subrecord(type, fields):
    rp = binaryparse.record_parser(type, fields)

    def parser(bstr):
        print(type)
        s, hdr, bstr = subrecord_header(bstr)
        if not s:
            return False, None, bstr

        print(type)
        print(hdr.type)
        assert(hdr.type == type.upper())

        s, data, rem = rp(bstr[:hdr.size])
        if not s:
            return False, None, bstr
        assert(rem == b'')

        return True, data, bstr[hdr.size:]
    return parser


def single_subrecord(type, record_type, definition, optional=False):
    subrecord_parser = binaryparse.record_parser("{}_{}".format(record_type, type), definition)
    def parser(bstr):
        s, hdr, rem = subrecord_header(bstr)
        if not s:
            return False, None, bstr

        if hdr.type != type.upper():
            if not optional:
                print("Expected {}, got {}".format(hdr.type, type))
            return optional, None, bstr

        return subrecord_parser(rem)

    return parser


def repeating_subrecord(type, record_type, definition):
    subrecord_parser = single_subrecord(type, record_type, definition, True)
    def parser(bstr):
        result = []

        while True:
            s, r, rem = subrecord_parser(bstr)
            if not s:
                return False, None, bstr

            if r is None:
                return True, result, bstr

            bstr = rem
            result.append(r)
    return parser


def record(type, definition):
    parsers = []
    for subrec_type, count, subrec_definition in definition:
        count = SubrecordCount(count)
        if count == SubrecordCount.REQUIRED:
            parser = single_subrecord(subrec_type, type, subrec_definition, False)
        elif count == SubrecordCount.OPTIONAL:
            parser = single_subrecord(subrec_type, type, subrec_definition, True)
        elif count == SubrecordCount.REPEATING:
            parser = repeating_subrecord(subrec_type, type, subrec_definition)
        else:
            raise ValueError("Unknown count parameter: {}".format(count))
        parsers.append((subrec_type, parser))

    return binaryparse.record_parser(type, parsers)


dial = record("dial", (
    ("edid", "-", (
        ("editorId", zstr),
    )),
    ("qsti", "*", (
        ("quests", formid),
    )),
    ("qstr", "*", (
        ("quests", formid),
    )),
    ("full", "-", (
        ("quests", zstr),
    )),
    ("data", "-", (
        ("dialType", byte),
    )),
))


def top_level(bstr):
    s, t, _ = record_type(bstr)
    assert(s)

    if t != 'GRUP':
        return header(bstr)
    else:
        return grup_header(bstr)
