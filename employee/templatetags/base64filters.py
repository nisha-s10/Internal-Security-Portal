import base64
from django import template

register = template.Library()

@register.filter(name="base64")
def base64_encode(value):
    """
    Encodes the given value in base64.
    """
    if isinstance(value, bytes):
        encoded = base64.b64encode(value).decode("utf-8")
    elif isinstance(value, str):
        encoded = base64.b64encode(value.encode("utf-8")).decode("utf-8")
    else:
        raise ValueError("Unsupported type for base64 encoding")
    return encoded
