from django import template
register = template.Library()

@register.filter
def is_none(value):
    if value is None:
        return True
    else:
        return False

@register.filter
def is_false(value):
    if value == False:
        return True
    else:
        return False

@register.filter
def multiply(value, arg):
    arg = float(arg)
    return int(value * arg)

@register.filter
def significantDigits(value, arg):
    arg = int(arg)
    formatter = "%0." + str(arg) + "g"
    return float(formatter % (value,))

@register.filter
def prepend(value, arg):
    return arg + value
