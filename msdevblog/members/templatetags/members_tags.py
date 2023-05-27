from typing import Any

from django import template


register = template.Library()


@register.filter
def value_or_empty(value: Any) -> Any | str:
    """
    Если переданное значение эквивалентно False,
    возвращает строку '----------------'
    иначе возвращает переданный элемент.
    """
    if not value:
        return '----------------'
    return value
