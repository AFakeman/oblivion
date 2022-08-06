import sys

from oblivion_types import header

FILENAME = sys.argv[1]

with open(FILENAME, 'rb') as f:
    esm = f.read()

c = 0

while True:
    s, result, rest = header(esm)

    if not s:
        raise ValueError("?")

    print(result)

    esm = rest[result.size:]

    if c == 99:
        break

    c += 1
