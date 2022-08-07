import sys

from pprint import pprint

from oblivion_types import record_or_grup_header, grup


FILENAME = sys.argv[1]


def quest_ids(group):
    result = {}
    for qust in group.records:
        assert(qust.header.type == "QUST")
        edid = list(filter(lambda x: x.type == "EDID", qust.subrecords))
        assert(len(edid) == 1)
        assert(qust.header.formid not in result)
        result[qust.header.formid] = edid[0].data.editorId
    return result


def get_topic(dial):
    topic = None
    for subrecord in dial.subrecords:
        if subrecord.type == 'EDID':
            assert(topic is None)
            topic = subrecord.data.editorId
    return topic

def dialogue_quests(group):
    result = {}
    topic = None
    for record in group.records:
        if record.header.type != 'GRUP':
            assert(record.header.type == 'DIAL')
            topic = get_topic(record)
            continue
        for info in record.records:
            assert(info.header.type == 'INFO')
            qsti = None
            responses = []
            for subrecord in info.subrecords:
                if subrecord.type == 'QSTI':
                    qsti = subrecord.data.questId
                elif subrecord.type == 'NAM1':
                    responses.append(subrecord.data.responseText)
            assert(qsti is not None)
            assert(topic is not None)
            idx = 1
            for response in responses:
                key = "{}_{}_{}_{}".format(qsti, topic, info.header.formid[2:].upper(), idx)
                result[key] = response
                idx += 1
    return result


quests = None
responses = None

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

        if header.label != b'DIAL' and header.label != b'QUST':
            f.seek(header.size - 20, 1)
            continue

        grup_data = f.read(header.size - 20)

        s, group, rest = grup(grup_data, header=header)
        assert(s)
        assert(rest == b'')

        if header.label == b'QUST':
            assert(quests is None)
            quests = quest_ids(group)
        elif header.label == b'DIAL':
            assert(responses is None)
            responses = dialogue_quests(group)

filenames = {}

for key, response in responses.items():
    quest_id, rem = key.split('_', 1)
    quest_name = quests[quest_id]
    filename = "{}_{}".format(quest_name, rem)
    filenames[filename] = response

pprint(filenames)
