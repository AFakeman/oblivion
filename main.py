import sys
import struct
import enum
from collections import namedtuple

FILENAME = sys.argv[1]

RecordHeader = namedtuple("Record", ["record_type", "size", "flags", "formid", "m"])
RecordType = namedtuple("RecordType", ["type", "format"])

RECORD = "<4sLLLL"

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


def read_struct(fmt, f, type=None):
    size = struct.calcsize(fmt)
    buf = f.read(size)
    if len(buf) == 0:
        raise ValueError("EOF")
    elif len(buf) != size:
        raise ValueError("OOPS")
    tup = struct.unpack(fmt, buf)
    if type is None:
        return tup

    return type._make(tup)


class Header():
    def __init__(self, nt):
        self.tuple = nt
        self.flags = [ flag for flat in Flags if fnt.flags & flag.value ]

    def __str__():
        return "Header {}, {} bytes, {}".format(self.tuple.record_type.decode('ASCII'), self.tuple.size, ", ".join([flag.name for flag in self.flags]))


def read_header(f):
    header_tuple = read_struct(RECORD, f, RecordHeader)
    header = Header(header_tuple)
    return header


with open(FILENAME, 'rb') as f:
    while True:
        header = read_struct(RECORD, f, RecordHeader)
        rec_type, size, flags, formid, _ = read_struct(RECORD, f)

        flag_list = [ flag.name for flag in Flags if flags & flag.value ]

        print("Record {}, {} bytes, {}".format(rec_type.decode('ASCII'), size,
            ", ".join(flag_list)))

        f.seek(size, 1)
