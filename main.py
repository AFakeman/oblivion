import sys

from oblivion_types import header

FILENAME = sys.argv[1]

with open(FILENAME, 'rb') as f:
    while True:
        header_bytes = f.read(20)

        if not header_bytes:
            break

        s, result, rest = header(header_bytes)

        if not s:
            raise ValueError("?")

        print(result)

        f.seek(result.size, 1)
