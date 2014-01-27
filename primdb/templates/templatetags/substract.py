from django import template
register = template.Library()
@register.filter
def substract(value, arg):
    return float(value) - float(arg)