import enum

import binaryparse

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

record_type = binaryparse.struct_parser("<4s")
unsigned_long = binaryparse.struct_parser("<L")

header_flags = binaryparse.enum_parser(unsigned_long, HeaderFlags)

header = binaryparse.record_parser("header", (
    ("type", record_type),
    ("size", unsigned_long),
    ("flags", header_flags),
    ("formid", unsigned_long),
    ("m", unsigned_long),
))
