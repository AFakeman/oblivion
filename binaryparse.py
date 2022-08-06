import enum
import struct
from collections import namedtuple


# Parser combinator is a map from a binary string to a tuple of result (bool),
# the parsed structure (an atom or a dict) and the remaining string.


def struct_parser(fmt):
    parser_obj = struct.Struct(fmt)
    size = parser_obj.size
    def parser(bstr):
        rest = bstr[size:]
        try:
            result = parser_obj.unpack_from(bstr)
            if len(result) == 1:
                result = result[0]
            s = True
        except Exception as e:
            result = None
            s = False
        return s, result, rest
    return parser


def str_parser(length, encoding="ascii"):
    sparser = struct_parser("<%ds" % length)
    def wrapper(bstr):
        s, result, rest = sparser(bstr)
        if s:
            result = result.decode(encoding)
        return s, result, rest

    return wrapper


# Record is a tuple or a list of two-tuples: field name and field parser
def record_parser(record):
    def parser(bstr):
        result = {}
        for field_name, field_parser in record:
            success, field_value, bstr = field_parser(bstr)
            if not success:
                return False, result, bstr
            result[field_name] = field_value
        return True, result, bstr

    return parser


def zstr_parser(encoding="ascii"):
    def parser(bstr):
        result = []
        for c in bstr:
            if c == 0:
                break
            result.append(c)
        else:
            return False, bytes(result), b''
        result = bytes(result).decode(encoding)
        rest = bstr[len(result)+1:]

        return True, result, rest
    return parser


def enum_parser(num_parser, enum):
    def parser(bstr):
        s, result, rest = num_parser(bstr)
        if not s:
            return s, result, rest

        assert(isinstance(result, int))

        result = {v for v in enum if v.value & result}

        return True, result, rest

    return parser
