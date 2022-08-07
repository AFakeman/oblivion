import sys

from oblivion_types import header, record_or_grup, dial, info


FILENAME = sys.argv[1]

with open(FILENAME, 'rb') as f:
    while True:
        header_bytes = f.read(20)

        if not header_bytes:
            break

        s, result, rest = record_or_grup(header_bytes)

        assert(s)

        print(result)

        if result.type != 'GRUP':
            f.seek(result.size, 1)
            continue

        if result.label != b'DIAL':
            f.seek(result.size - 20, 1)
            continue

        data = f.read(result.size - 20)

        while data:
            s, hdr, data = record_or_grup(data)
            assert(s)

            print(hdr)

            if hdr.type == 'DIAL':
                s, d, data = dial(data)
                assert(s)
                print(d)
            elif hdr.type == 'GRUP':
                s, h, buf = header(data)
                print(h)
                s, d, _ = info(buf)
                print(d)
                data = data[hdr.size - 20:]
            else:
                data = data[hdr.size:]
