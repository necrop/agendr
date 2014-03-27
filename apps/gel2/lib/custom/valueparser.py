
def value_parser(value, type):
    """Coerces a field value (probably a string) into an appropriate
    type, given the designated type of the field to which it belongs.

    E.g. if the field is a 'boolean' type, then the value will be coerced
    to True, False, or None.

    Any value of '', 'null', or 'none' is coerced to None, regardless
    of the field type.

    Arguments: value, field-type
    """

    if value is None:
        return None

    value = str(value).strip()

    if value.lower() in ("none", "null", ""):
        return None

    elif type in ("integer", "int"):
        try:
            return int(value)
        except ValueError:
            return 0

    elif type == "float":
        try:
            return float(value)
        except ValueError:
            return float(0)

    elif type in ("boolean", "bool"):
        if value.lower() in ("true", "yes", "1"):
            return True
        else:
            return False

    return value
