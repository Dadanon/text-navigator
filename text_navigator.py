import os.path
import time
from typing import List
from typing import Dict as _

import docx
import pymupdf

from exceptions import *
from general import NavOption, get_docx_content

a = _[int, int]
class TextNavigator:
    _nav_option: NavOption  # Опция навигации - страница или абзац
    _file_path: str  # Путь к текстовому файлу
    _file_content: str  # Содержимое файла
    _extension: str  # Расширение файла
    _par_positions: List[int]  # Позиции параграфов
    _page_positions: List[int]  # Позиции страниц

    def __init__(self, text_file_path: str):
        self._par_positions = []
        self._page_positions = []
        self._file_content = ''
        self._nav_option = NavOption.PARAGRAPH
        if not os.path.exists(text_file_path):
            raise FileNotFoundError(f'Не найден файл по пути: {text_file_path}')
        last_dot_position = text_file_path.rfind('.')
        if last_dot_position == -1:
            raise ExtensionAbsentError(f'Отсутствует расширение файла: {text_file_path}')
        self._file_path = text_file_path
        self._extension = self._file_path[last_dot_position:]
        match self._extension:
            case '.docx':
                self._set_docx_content()
            case '.pdf' | '.epub' | '.fb2':
                self._set_pypdf_content()
            case _:
                raise UnsupportedFormatError(f'Неподдерживаемое расширение файла: {self._file_path}')
        # print(self._file_content)
        print('\n\nParagraph positions:\n\n')
        print(self._par_positions)
        print('\n\nPage positions:\n\n')
        print(self._page_positions)
        print(f'\n\nFile content with one page: {self._file_content[305:423]}')
        print(f'\n\nFile content with one page: {self._file_content[423:2199]}')
        print(f'\n\nFile content with one page: {self._file_content[13154:15492]}')
        # print(f'\n\nFile content with one page: {self._file_content[13154:13530]}')
        # print(f'\n\nFile content with one page: {self._file_content[13892:14137]}')

    # INFO: private methods

    # INFO: setting content for different formats block

    def _set_docx_content(self):
        document: docx.Document = docx.Document(self._file_path)
        content_chunks = []
        current_position: int = 0
        for par in document.paragraphs:
            content_chunks.append(par.text)
            for i in range(len(par.runs)):
                if 'lastRenderedPageBreak' in par.runs[i]._element.xml:
                    runs_before = par.runs[:i]
                    runs_before_length = 0 if len(runs_before) == 0 else sum(
                        map(lambda run: len(run.text), runs_before))
                    self._page_positions.append(current_position + runs_before_length)
            self._par_positions.append(current_position)
            current_position += len(par.text) + 1
        current_position -= 1  # Удаляем последний символ, т.к. следующая строка с join не добавляет \n в конце
        self._file_content = '\n'.join(content_chunks)
        # print(f'File content length: {len(self._file_content)}, current position: {current_position}, file_content: \n\n{self._file_content[1069:1139]}')

    def _set_pypdf_content(self):
        doc = pymupdf.open(self._file_path)
        index = -1
        text_position = 0
        par_blocks = []
        for page in doc:  # iterate the document pages
            index += 1
            page_blocks = page.get_textpage().extractBLOCKS()
            page_blocks_sorted = sorted(page_blocks, key=lambda coords: (coords[3], coords[0]))
            page_blocks_mapped = map(lambda block: block[4].replace('\n', ' '), page_blocks_sorted)
            for block in page_blocks_mapped:
                text_position += len(block)
                self._par_positions.append(text_position)
                par_blocks.append(block)
            self._page_positions.append(text_position)
        self._file_content = ''.join(par_blocks)

    # def _set_epub_content(self):
    #     doc = pymupdf.open(self._file_path)
    #     for page in doc:
    #         print(f'\n\nCurrent page:\n\n{page.get_textpage().extractBLOCKS()}')

    # INFO: end block

    @property
    def _nav_positions(self) -> List[int]:
        match self._nav_option:
            case NavOption.PARAGRAPH:
                return self._par_positions
            case NavOption.PAGE:
                return self._page_positions
            case _:
                raise UnknownNavOptionError("Неизвестная опция навигации")

    def _get_next_position(self, position: int):
        for pos in self._nav_positions:
            if pos > position:
                return pos
        return -1

    def _get_prev_position(self, position: int):
        for pos in reversed(self._nav_positions):
            if pos < position:
                return pos
        return -1

    # INFO: public methods

    def set_nav_option(self, option: NavOption):
        """Установить опцию навигации - на данный момент страница или параграф"""
        self._nav_option = option

    def get_next_pos(self, position: int) -> int:
        """Возвращает позицию начала следующей опции навигации
        (параграфа или страницы) в тексте после position"""
        return self._get_next_position(position)

    def get_prev_pos(self, position: int) -> int:
        """Возвращает позицию начала предыдущей опции навигации
        (параграфа или страницы) в тексте после position"""
        return self._get_prev_position(position)

    def get_file_content(self) -> str:
        """
        Вспомогательный метод для уверенности, что читаемое содержимое
        и содержимое для поиска позиций навигации созданы единообразно
        """
        return self._file_content


def test_navigator(file_path: str):
    start_time = time.time()
    navigator = TextNavigator(file_path)
    # print(navigator.get_next_pos(1069))
    # navigator.set_nav_option(NavOption.PAGE)
    # print(navigator.get_next_pos(1069))
    end_time = time.time()
    print(f'Total time: {(end_time - start_time)}')


test_navigator(os.path.abspath('test_files/fb2.fb2'))
