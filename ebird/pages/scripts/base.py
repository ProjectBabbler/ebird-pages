import datetime
import json


class JSONDateEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime.date):
            return o.isoformat()
        if isinstance(o, datetime.time):
            return o.isoformat()
        if isinstance(o, datetime.timedelta):
            return str(o)
        else:
            super().default(o)


def save(fp, values, indent):
    """Save the JSON data to a file or stdout.

    :param fp: the writer.
    :param values: the python data to be saved.
    :param indent: the level of indentation when prettyprinting the output.

    """
    fp.write(json.dumps(values, indent=indent, cls=JSONDateEncoder).encode('utf-8'))
    if fp.name == '<stdout>':
        fp.write(b'\n')
