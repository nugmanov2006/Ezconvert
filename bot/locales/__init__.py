from locales.ru import RU_TEXTS
from locales.en import EN_TEXTS

TEXTS = {
    'ru': RU_TEXTS,
    'en': EN_TEXTS
}

def get_text(lang: str, key: str, **kwargs) -> str:
    text = TEXTS.get(lang, TEXTS['ru']).get(key, key)
    return text.format(**kwargs) if kwargs else text