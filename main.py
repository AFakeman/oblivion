import sys

from oblivion_types import record_or_grup_header, grup


FILENAME = sys.argv[1]

with open(FILENAME, 'rb') as f:
    while True:
        header_bytes = f.read(20)

        if not header_bytes:
            break

        s, header, rest = record_or_grup_header(header_bytes)

        assert(s)
        assert(rest == b'')

        if header.type != 'GRUP':
            f.seek(header.size, 1)
            continue

        if header.label != b'DIAL':
            f.seek(header.size - 20, 1)
            continue

        grup_data = f.read(header.size - 20)
        s, grup, rest = grup(grup_data, header=header)
        assert(s)
        assert(rest == b'')
        for record in grup.records:
            print(record)
