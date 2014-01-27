from django import template
register = template.Library()
@register.filter
def split(value, sep = "_"):
    parts = value.split(sep)
    return (parts[0],sep.join(parts[1:]))