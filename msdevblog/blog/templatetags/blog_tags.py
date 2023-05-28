from django import template

register = template.Library()

FIELD_LENGTH = 117


@register.filter
def extra_space(value: str) -> str:
    """
    Добавляет дополнительные пробелы если комментарий слишком короткий,
    с целью лучшего отображения короткого текста на странице.
    Для отключения свертывания пробелов в Html необходимо установить
    CSS свойство "white-space: pre-wrap;"
    """
    return value + ' ' * (FIELD_LENGTH - input_len) + '~' if (input_len := len(value)) < FIELD_LENGTH else value
