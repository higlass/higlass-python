import json

PRELUDE = """
from typing import Protocol, Union, Any, Dict

class T(Protocol):
    options: Union[Dict[str, Any], None]
    type: str

    def copy(self) -> 'T':
        ...

class _TrackTypeMixen:

"""

METHOD = """
    def {method}(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "{name}"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy
"""


def name_to_method(name: str) -> str:
    head, *parts = name.split('-')
    # rotate 1d/2d prefix to end of name
    if head == '1d' or head == '2d':
        parts.append(head)
    else:
        parts = [head] + parts
    return "_".join(parts)


def main():
    with open('schema.json') as f:
        schema = json.load(f)
        names = schema['definitions']['tracks']['enum_track']['properties']['type']['enum']

    with open('hg/mixins.py', mode='w') as f:
        f.write(PRELUDE)

        for name in names:
            method = name_to_method(name)
            f.write(METHOD.format(method=method, name=name))


if __name__ == "__main__":
    main()
