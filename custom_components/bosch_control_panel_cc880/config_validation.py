"""Config validation for bosch_control_panel_cc880 integration."""

from dataclasses import dataclass


@dataclass
class SchemaType:
    """Define a type of schema for presentation and validation.

    Validation is optional. If not provided, then presentation will be always used
    """

    presentation: type
    validation: type = None


class SchemaTypes:
    """Manage a set of schema types."""

    def __init__(self, schemas: dict[str, SchemaType]) -> None:
        """Start the schema manager."""
        self.schemas: dict[str, SchemaType] = schemas

    def _get_schema(self, key: str = None, validation: bool = False):
        if key:
            schema = self.schemas[key]
            if schema.validation and validation:
                return schema.validation
            return schema.presentation

        schemas = {}
        for _key, schema in self.schemas.items():
            if schema.validation and validation:
                schemas[_key] = schema.validation
            else:
                schemas[_key] = schema.presentation
        return schemas

    def get_schemas(self, validation: bool = False) -> dict[str, SchemaType]:
        """Get the presentation or validation schemas."""
        return self._get_schema(validation=validation)

    def get_schema(self, key: str, validation: bool = False) -> SchemaType:
        """Get a single schema type given its key."""
        return self._get_schema(key=key, validation=validation)
