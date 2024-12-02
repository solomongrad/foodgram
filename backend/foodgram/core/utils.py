from shortuuid import ShortUUID

from core.constants import SHORT_LINK_LENGTH


def generate_short_link() -> str:
    """Генерирует обрезанный до N знаков ShortUUID."""
    suid = ShortUUID(alphabet="0123456789abcdefghijklmnopqrstuvwxyz")
    return suid.random(length=SHORT_LINK_LENGTH)
