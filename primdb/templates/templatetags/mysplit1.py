from django import template
register = template.Library()
@register.filter
def mysplit1(value, sep = "|"):
    parts = value.split(sep)
    return (parts[0], parts[1], sep.join(parts[2:]))