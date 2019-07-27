from django import template
from django.utils.safestring import mark_safe

register = template.Library()   # register的名字是固定的,不可改变


@register.simple_tag
def __all__errors(errors):
    """通过form表单中__all__"""
    for k, v in errors.items():
        if k == "__all__":
            return v

