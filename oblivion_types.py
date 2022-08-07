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


zstring = binaryparse.zstr_parser('cp1252')
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
dialog_type = binaryparse.enum_parser(unsigned_byte, DialogTypes)
dialog_type_short = binaryparse.enum_parser(unsigned_short, DialogTypes)
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
    ("formid", formid),
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


subrecords = {}
subrecord_namedtuple = namedtuple('subrecord', ["type", "data"])


def subrecord(record_type, bstr):
    s, h, r = subrecord_header(bstr)
    if not s:
        return s, None, bstr

    parser_name = "{}_{}".format(record_type, h.type)

    if parser_name not in subrecords:
        result = subrecord_namedtuple._make((h.type, r[:h.size]))
        return True, result, r[h.size:]

    bstr = r

    s, r, b = subrecords[parser_name](bstr)
    if not s:
        return s, None, bstr
    result = subrecord_namedtuple._make((h.type, r))

    bstr = b

    return True, result, bstr


def subrecord_type(record_type, type, definition):
    parser_name = "{}_{}".format(record_type, type)
    parser = binaryparse.record_parser(parser_name, definition)
    subrecords[parser_name] = parser
    return parser


def record_subrecords(type, definition):
    for subrecord_t, subrecord_definition in definition:
        subrecord_type(type, subrecord_t, subrecord_definition)

record_namedtuple = namedtuple('record', ["header", "subrecords"])
def record(bstr):
    s, h, r = header(bstr)
    if not s:
        return s, None, b''

    bstr = r

    record_data = bstr[:h.size]
    subrecords = []

    while len(record_data) > 0:
        s, sub, r = subrecord(h.type, record_data)
        if not s:
            return s, None, b''

        subrecords.append(sub)
        record_data = r

    result = record_namedtuple._make((h, tuple(subrecords)))

    return True, result, bstr[h.size:]


def record_or_grup(bstr):
    s, t, _ = record_type(bstr)
    assert(s)

    if t != 'GRUP':
        return header(bstr)
    else:
        return grup_header(bstr)


grup_namedtuple = namedtuple("grup", ("header", "records"))


def grup(bstr):
    s, h, _ = grup_header(bstr)

    if not s:
        return s, None, b''

    data = bstr[20:h.size]

    records = []

    while len(data) > 0:
        s, r, data = record(data)
        if not s:
            return s, None, b''
        records.append(r)

    result = grup_namedtuple._make((h, records))

    return True, result, bstr[h.size:]



record_subrecords("DIAL", (
    ("EDID", (
        ("editorId", zstring),
    )),
    ("QSTI", (
        ("quests", formid),
    )),
    ("QSTR", (
        ("quests", formid),
    )),
    ("FULL", (
        ("fullName", zstring),
    )),
    ("DATA", (
        ("dialType", dialog_type),
    )),
))


record_subrecords("INFO", (
    ("DATA", (
        ("dialogType", dialog_type_short),
        ("dialogFlags", response_flags),
    )),
    ("QSTI", (
        ("questId", formid),
    )),
    ("PNAM", (
        ("previousId", formid),
    )),
    ("TRDT", (
        ("emotionType", emotion_type),
        ("emotionValue", long_t),
        ("unknown", binaryparse.skip_parser(4)),
        ("responseNumber", unsigned_byte),
        ("unknown2", binaryparse.skip_parser(3)),
    )),
    ("NAM1", (
        ("responseText", zstring),
    )),
    ("NAM2", (
        ("actorNotes", zstring),
    )),
))
