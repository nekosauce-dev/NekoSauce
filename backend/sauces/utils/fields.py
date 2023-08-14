from django.db import models


class BitField(models.Field):
    def __init__(self, *args, max_length=None, **kwargs):
        self.max_length = max_length
        super().__init__(*args, **kwargs)

    def db_type(self, connection):
        if connection.vendor == "postgresql":
            if self.max_length is not None:
                return f"bit({self.max_length})"
            return "bit"
        return super().db_type(connection)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        # Convert the bit string to an integer or some other appropriate representation
        return int(value, 2)

    def to_python(self, value):
        if value is None:
            return value
        # Convert the integer value to a bit string
        return bin(value)[2:]

    def get_prep_value(self, value):
        if value is None:
            return value
        # Ensure the value is a bit string
        return bin(int(value, 2))[2:]
