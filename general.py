from enum import IntEnum


class NavOption(IntEnum):
    PARAGRAPH = 0
    PAGE = 1


SUPPORTED_FORMATS = [
    'txt',
    'rtf',
    'doc',
    'docx',  # Ready
    'odt',
    'htm',
    'html',
    'xml',
    'pdf',  # Ready
    'fb2',  # Ready
    'epub'  # Ready
]
"""Список будет дополняться со временем"""


# def try_open_txt(file_path: str) -> str:
#     encodings = ['windows-1251', 'utf-8', 'utf-16-be', 'utf-16-le', 'koi8-r', 'mac-cyrillic', 'iso8859-5', 'cp866']
#     for encoding in encodings:
#         try:
#             with open(file_path, 'r', encoding=encoding) as file:
#                 return file.read()
#         except (UnicodeDecodeError, LookupError):
#             continue
#     raise Exception(f"Кодировка файла {file_path} не найдена в списке {encodings}"


# def read_html_xml(file_name):
#     with open(file_name, 'r', encoding='utf-8') as file:
#         text = file.read()
#         return re.sub('<[^<]+?>', '', text)
