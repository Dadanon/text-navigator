import datetime
import os.path
import time
from zipfile import ZipFile
from xml.etree import ElementTree as ET

from exceptions import *
from general import NavOption, try_open_txt, read_docx, read_pdf, read_epub, read_html_xml, read_python_docx


class TextNavigator:
    _nav_option: NavOption  # Опция навигации - страница или абзац
    _file_path: str  # Путь к текстовому файлу
    _file_content: str  # Содержимое файла

    def __init__(self, text_file_path: str):
        self._nav_option = NavOption.PARAGRAPH
        if not os.path.exists(text_file_path):
            raise FileNotFoundError(f'Не найден файл по пути: {text_file_path}')
        last_dot_position = text_file_path.rfind('.')
        if last_dot_position == -1:
            raise ExtensionAbsentError(f'Отсутствует расширение файла: {text_file_path}')
        file_extension: str = text_file_path[last_dot_position:]
        match file_extension:
            case '.txt':
                file_content = try_open_txt(text_file_path)
            case '.docx':
                file_content = read_python_docx(text_file_path)
            case '.pdf':
                file_content = read_pdf(text_file_path)
            case ('.htm', 'html', '.xml'):
                file_content = read_html_xml(text_file_path)
            case '.epub':
                file_content = read_epub(text_file_path)
            case _:
                raise UnsupportedFormatError(f'Неподдерживаемое расширение файла: {text_file_path}')
        self._file_content = file_content
        print(self._file_content)


def test_navigator(file_path: str):
    navigator = TextNavigator(file_path)


start_time = time.time()
test_navigator(os.path.abspath('test_files/docx.docx'))
end_time = time.time()
print(f'Total time: {(end_time - start_time)}')

# start_time = time.time()
# for file_name in os.listdir('test_files'):
#     test_navigator(os.path.abspath(f'test_files/{file_name}'))
# end_time = time.time()
# print(f'Total time: {end_time - start_time}')
