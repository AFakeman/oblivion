import enum
from collections import namedtuple

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


class DialogTypes(enum.Enum):
    TOPIC = 0
    CONVERSATION = 1
    COMBAT=2
    PERSUASION=3
    DETECTION=4
    SERVICE=5
    MISCELLANEOUS=6


class ResponseFlags(enum.Enum):
    GOODBYE = 0x0001
    RANDOM = 0x0002
    SAY_ONCE = 0x0004
    RUN_IMMEDIATELY = 0x0008
    INFO_REFUSAL = 0x0010
    RANDOM_END = 0x0020
    RUN_FOR_RUMORS = 0x0040


class EmotionType(enum.Enum):
    NEUTRAL = 0
    ANGER = 1
    DISGUST = 2
    FEAR = 3
    SAD = 4
    HAPPY = 5
    SURPRISE = 6


zstr = binaryparse.zstr_parser('cp1252')
record_type = binaryparse.str_parser(4)
grup_label = binaryparse.struct_parser('<4s')
unsigned_long = binaryparse.struct_parser("<L")
long_t = binaryparse.struct_parser("<l")
float_t = binaryparse.struct_parser("<f")

formid = unsigned_long
unsigned_short = binaryparse.struct_parser("<H")
byte = binaryparse.struct_parser("<b")
unsigned_byte = binaryparse.struct_parser("<B")

header_flags = binaryparse.flag_parser(unsigned_long, HeaderFlags)
dialog_type = binaryparse.enum_parser(unsigned_short, DialogTypes)
response_flags = binaryparse.flag_parser(byte, ResponseFlags)
emotion_type = binaryparse.flag_parser(long_t, EmotionType)


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
                print("Expected {}, got {}".format(type, hdr.type))
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


info_data = single_subrecord("data", "info", (
    ("dialogType", dialog_type),
    ("dialogFlags", response_flags),
))

info_qsti = single_subrecord("qsti", "info", (
    ("quests", formid),
))

info_pnam = single_subrecord("pnam", "info", (
    ("quests", formid),
), True)

info_trdt = single_subrecord("trdt", "info", (
    ("emotion_type", emotion_type),
    ("emotion_value", long_t),
    ("unknown", binaryparse.skip_parser(4)),
    ("response_number", unsigned_byte),
    ("unknown2", binaryparse.skip_parser(3)),
), True)

info_nam1 = single_subrecord("nam1", "info", (
    ("response_text", zstr),
), True)

info_nam2 = single_subrecord("nam2", "info", (
    ("actor_notes", zstr),
), True)

info_namedtuple = namedtuple("info", (
    "data",
    "qsti",
    "pnam",
    "trdt",
    "nam1",
    "nam2",
))


info_records = (
        info_data,
        info_qsti,
        info_pnam,
)


info_funni_records = (
        info_trdt,
        info_nam1,
        info_nam2,
)


def info(bstr):
    result = []
    for rec in info_records:
        s, r, rem = rec(bstr)
        if not s:
            return s, r, bstr
        bstr = rem
        result.append(r)
    lists = [[] for rec in info_funni_records]
    while True:
        br = False
        idx = 0
        for rec in info_funni_records:
            s, r, rem = rec(bstr)
            if not s:
                return s, r, bstr
            if r is None:
                br = True
                break
            lists[idx].append(r)
            bstr = rem
            idx += 1
        if br:
            break
    return True, info_namedtuple._make(result + lists), bstr


def top_level(bstr):
    s, t, _ = record_type(bstr)
    assert(s)

    if t != 'GRUP':
        return header(bstr)
    else:
        return grup_header(bstr)
