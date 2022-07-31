import sys
import struct
import enum
from collections import namedtuple

from oblivion_types import Flags, oblivion_parser

FILENAME = sys.argv[1]

with open(FILENAME, 'rb') as f:
    while True:
        header_bytes = f.read(oblivion_parser.sizeof("record_header"))
        if header_bytes == b"":
            break

        header = oblivion_parser.parse_from_bytes("record_header", header_bytes)

        flag_list = [ flag.name for flag in Flags if header.flags & flag.value ]

        print("Record {}, {} bytes, {}".format(header.type.decode('ASCII'), header.size,
            ", ".join(flag_list)))

        f.seek(header.size, 1)
