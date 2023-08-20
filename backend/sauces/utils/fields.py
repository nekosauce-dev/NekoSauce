from django.db import models


class BitField(models.Field):
    def db_type(self, connection):
        if connection.vendor == "postgresql":
            if self.max_length is not None:
                return f"bit({self.max_length})"
            return "bit"
        return super().db_type(connection)

    def from_db_value(self, value, expression, connection):
        return value

    def to_python(self, value):
        if value is None:
            return value
        # Convert the integer value to a bit string
        return value

    def get_prep_value(self, value):
        if value is None:
            return value

        # Ensure the value is a bit string
        for bit in value:
            if bit not in ["0", "1"]:
                raise ValueError(f"Invalid bit value: {bit}")

        return value
