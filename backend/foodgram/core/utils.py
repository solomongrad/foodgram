from uuid import uuid4


def generate_short_link() -> str:
    """Генерирует обрезанный до N знаков UUID4."""

    return uuid4().hex[:6]