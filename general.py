from enum import IntEnum


class NavOption(IntEnum):
    PARAGRAPH = 0
    PAGE = 1


LINES_ON_HTML_PAGE = 52  # В Word на странице максимум 52 строки (Arial, 12pt)
LINE_LENGTH_MAX = 120  # В Word длина строки максимум 120 символов (Arial, 12pt)


SUPPORTED_FORMATS = [
    'txt',
    'rtf',  # Ready
    'doc',  # Ready (presumably)
    'docx',  # Ready
    'odt',  # Ready
    'htm',  # Ready
    'html',  # Ready
    'xml',  # Ready
    'pdf',  # Ready
    'fb2',  # Ready
    'epub'  # Ready
]
"""Список будет дополняться со временем"""


def try_open_txt(file_path: str) -> str:
    encodings = ['windows-1251', 'utf-8', 'utf-16-be', 'utf-16-le', 'koi8-r', 'mac-cyrillic', 'iso8859-5', 'cp866']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                return file.read()
        except (UnicodeDecodeError, LookupError):
            continue
    raise Exception(f"Кодировка файла {file_path} не найдена в списке {encodings}")
