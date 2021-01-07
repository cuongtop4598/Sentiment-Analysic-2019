from django import template

register = template.Library()

@register.filter(name='filterBrand')
def filterBrand(obj,value):
    return obj.get(pk=value).trademark

@register.filter(name='filterPhone')
def filterPhone(obj,value):
    return obj.filter(value)

