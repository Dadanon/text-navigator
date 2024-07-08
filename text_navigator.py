import os.path

from exceptions import UnsupportedFormatError
from general import NavOption, SUPPORTED_FORMATS


class TextNavigator:
    _nav_option: NavOption
    _file_path: str

    def __init__(self, text_file_path: str):
        self._nav_option = NavOption.PARAGRAPH
        if not os.path.exists(text_file_path):
            raise FileNotFoundError(f'Не найден файл по пути: {text_file_path}')
        file_extension = text_file_path.split('.')[-1]
        if file_extension not in SUPPORTED_FORMATS:
            raise UnsupportedFormatError(f'Неподдерживаемое расширение файла: {text_file_path}')
        self._file_path = text_file_path
