import enum
import struct
from collections import namedtuple


class Endianness(enum.Enum):
    LITTLE = "<"

class BinaryParser:
    def __init__(self, endian=Endianness.LITTLE, prefix=''):
        self._endian = endian.value

        # when registering namedtuple classes, prefix the type name with this
        self._prefix = prefix

        # a map from type name to its corresponding format in the struct module
        self._types = {
                "char": "b",
                "unsigned long": "L",
        }

        # a map from type name to the list of the type/field tuples. default
        # types are not present here.
        self._fields = {}

        # a map from class name to the record class. primitive types have no
        # class.
        self._classes = {}

    # the definition is the raw struct module format string, should only be one
    # field, e.g. 4s. for multi-field definitions use register.
    def typedef(self, type_name, definition):
        if type_name in self._types:
            raise ValueError("Type {} is already registered".format(type_name))
        self._types[type_name] = definition

    # the definition is an array of tuples, first element of the tuple is the
    # field type, the second is the type of the field. This can reference
    # previously added types.
    def register(self, type_name, definition):
        if type_name in self._types:
            raise ValueError("Type {} is already registered".format(type_name))
        format = self._generate_format(definition)
        # we just copy the definition as-is.
        self._fields[type_name] = [(k, v) for k, v in definition]
        self._types[type_name] = format
        self._classes[type_name] = self._create_tuple_for_type(type_name)

    def field_count(self, type_name):
        if type_name not in self._types:
            raise ValueError("Type {} does not exist".format(type_name))
        # if a type is not in fields, it is a primitive type that only contains
        # one field.
        if type_name not in  self._fields:
            return 1
        count = 1
        return sum(self.field_count(type) for type, name in self._fields[type_name])

    # size of a type in bytes
    def sizeof(self, type_name):
        return struct.calcsize(self.format_for_type(type_name))

    # turn our definition format into a struct format string
    def _generate_format(self, definition):
        format_list = [self._endian]
        for field_type, field_name in definition:
            if field_type not in self._types:
                raise ValueError("Type {} does not exist".format(field_type))
            format_list.append(self._types[field_type])
        return "".join(format_list)

    # return struct format for a type
    def format_for_type(self, type_name):
        if type_name not in self._types:
            raise ValueError("Type {} does not exist".format(type_name))
        return self._types[type_name]

    # create a namedtuple class for a given type
    def _create_tuple_for_type(self, type_name):
        if type_name not in self._types:
            raise ValueError("Type {} does not exist".format(type_name))
        return namedtuple(self._prefix + type_name, [v for k, v in self._fields[type_name]])

    # parse a given type from a bytes buffer
    def parse_from_bytes(self, type_name, buf):
        fmt = self.format_for_type(type_name)
        tup = struct.unpack(fmt, buf)
        return self.parse_from_tuple(type_name, tup)

    # parse a given type from a tuple. mostly for internal use.
    def parse_from_tuple(self, type_name, tup):
        assert(len(tup) == self.field_count(type_name))
        if type_name not in self._types:
            raise ValueError("Type {} does not exist".format(type_name))

        if type_name not in self._fields:
            return tup[0]

        parsed_tuple = []
        idx = 0

        for field_type, field_name in self._fields[type_name]:
            count = self.field_count(field_type)
            start = idx
            end = idx + count
            subtuple = tup[start:end]
            idx = end
            value = self.parse_from_tuple(field_type, subtuple)
            parsed_tuple.append(value)

        return self._classes[type_name]._make(parsed_tuple)


if __name__ == "__main__":
    parser = BinaryParser()
    print(parser._types)
    parser.typedef("record_type", "4s")
    print(parser._types)
    parser.register("header", [
        ("record_type", "type"),
        ("unsigned long", "size"),
        ("unsigned long", "flags"),
        ("unsigned long", "formid"),
        ("unsigned long", "m"),
    ])
    print(parser._types)
    print(parser._classes)
