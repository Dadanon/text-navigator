from enum import IntEnum
from typing import Tuple
from charset_normalizer import from_path


class NavOption(IntEnum):
    PARAGRAPH = 0
    PAGE = 1


LINES_ON_HTML_PAGE = 52  # В Word на странице максимум 52 строки (Arial, 12pt)
LINE_LENGTH_MAX = 120  # В Word длина строки максимум 120 символов (Arial, 12pt)

SUPPORTED_FORMATS = [
    'txt',  # Ready
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


def try_open_txt(file_path: str) -> Tuple[str, str]:
    encodings = ['cp1251', 'utf-8', 'utf-16-be', 'utf-16-le', 'koi8-r', 'mac-cyrillic', 'iso8859-5', 'cp866']

    results = from_path(file_path, cp_isolation=encodings)
    guess_result = results.best()
    file_content = str(guess_result)
    file_encoding = guess_result.encoding
    return file_content, file_encoding
