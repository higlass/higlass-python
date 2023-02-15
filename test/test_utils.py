from __future__ import annotations

import pytest
from higlass._utils import copy_unique, ensure_list
from pydantic import BaseModel


def test_copy_unique():
    class Person(BaseModel):
        name: str

    person = Person(name="foo")

    other = copy_unique(person)
    assert other is not person
    assert not hasattr(other, "uid")

    class PersonWithId(Person):
        uid: str

    person_with_id = PersonWithId(name="foo", uid="something")
    other = copy_unique(person_with_id)
    assert other is not person
    assert hasattr(other, "uid")
    assert other.uid != person_with_id.uid


@pytest.mark.parametrize("value", [1, [1, 2], None])
def test_ensure_list(value: int | list[int] | None):
    assert isinstance(ensure_list(value), list)
