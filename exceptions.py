class UnsupportedFormatError(Exception):
    """Использование формата текстового файла, не указанного в ГОСТ"""
    pass


class ExtensionAbsentError(Exception):
    """Отсутствие расширения у файла, текстовое содержимое которого собираемся получить"""
    pass


class UnknownNavOptionError(Exception):
    """Использование опции навигации, отличной от абзаца или страницы"""
    pass


class ODTError(Exception):
    """Специфическая ошибка ODT файла (гипотетическая), связанная с отсутствием файла content.xml внутри архива"""
    pass
