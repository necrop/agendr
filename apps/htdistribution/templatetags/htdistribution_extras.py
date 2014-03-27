from django import template
register = template.Library()

@register.filter
def significantDigits(value, arg):
    arg = int(arg)
    formatter = "%0." + str(arg) + "g"
    return float(formatter % (value,))
