from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar, Union

import pydantic_core.core_schema as core_schema
from pydantic import BaseModel, TypeAdapter
from pydantic.json_schema import GenerateJsonSchema, JsonSchemaMode, JsonSchemaValue

if TYPE_CHECKING:
    from typing import TypeGuard

### Vendored from pydantic._internal._core_utils

CoreSchemaField = Union[
    core_schema.ModelField,
    core_schema.DataclassField,
    core_schema.TypedDictField,
    core_schema.ComputedField,
]

CoreSchemaOrField = Union[core_schema.CoreSchema, CoreSchemaField]

_CORE_SCHEMA_FIELD_TYPES = {
    "typed-dict-field",
    "dataclass-field",
    "model-field",
    "computed-field",
}


def is_core_schema(
    schema: CoreSchemaOrField,
) -> TypeGuard[core_schema.CoreSchema]:
    return schema["type"] not in _CORE_SCHEMA_FIELD_TYPES


### End vendored code


class _GenerateJsonSchema(GenerateJsonSchema):
    def field_title_should_be_set(self, schema: CoreSchemaOrField) -> bool:
        """Check if the title should be set for a field.

        Override the default implementation to not set the title for core
        schemas. Makes the final schema more readable by removing
        redundant titles. Explicit Field(title=...) can still be used.
        """
        return_value = super().field_title_should_be_set(schema)
        if return_value and is_core_schema(schema):
            return False
        return return_value

    def nullable_schema(self, schema: core_schema.NullableSchema) -> JsonSchemaValue:
        """Generate a JSON schema for a nullable schema.

        This overrides the default implementation to ignore the nullable
        and generate a more simple schema. All the Optional[T] fields
        are converted to T (instead of the
        default {"anyOf": [{"type": "null"}, {"type": "T"}]}).
        """
        return self.generate_inner(schema["schema"])

    def default_schema(self, schema: core_schema.WithDefaultSchema) -> JsonSchemaValue:
        """Generate a JSON schema for a schema with a default value.

        Similar to above, this overrides the default implementation to
        not explicity set {"default": null} in the schema when the field
        is Optional[T] = None.
        """
        if schema.get("default") is None:
            return self.generate_inner(schema["schema"])
        return super().default_schema(schema)

    def generate(
        self, schema: core_schema.CoreSchema, mode: JsonSchemaMode = "validation"
    ) -> JsonSchemaValue:
        """Generate a JSON schema.

        This overrides the default implementation to remove the titles
        from the definitions. This makes the final schema more readable.
        """

        json_schema = super().generate(schema, mode=mode)
        # clear the titles from the definitions
        for d in json_schema.get("$defs", {}).values():
            d.pop("title", None)
        return json_schema


# Schema modifiers
ModelT = TypeVar("ModelT", bound=BaseModel)


def get_schema_of(type_: object):
    return TypeAdapter(type_).json_schema(schema_generator=_GenerateJsonSchema)


def simplify_enum_schema(schema: dict[str, Any]):
    # reduce union of enums into single enum
    if "anyOf" in schema:
        enum = []
        for entry in schema["anyOf"]:
            assert "enum" in entry
            enum.extend(entry["enum"])
        return {"enum": enum}

    enum = schema["enum"]

    # if there is only one enum entry, make it a const
    if len(enum) == 1:
        return {"const": enum[0]}

    return {"enum": enum}
