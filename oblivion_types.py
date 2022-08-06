import enum

import binaryparse

class Flags(enum.Enum):
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


oblivion_parser = binaryparse.BinaryParser()

RecordHeader = [
        ("record_type", "type"),
        ("unsigned long", "size"),
        ("unsigned long", "flags"),
        ("unsigned long", "formid"),
        ("unsigned long", "m"),
]

GrupSubheader = [
        ("record_type", "type"),
        ("unsigned long", "size"),

]

oblivion_parser.typedef("record_type", "4s")

oblivion_parser.register("record_header", RecordHeader)
