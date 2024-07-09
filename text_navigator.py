import os.path
import re
import time
from typing import List

import docx

from exceptions import *
from general import NavOption


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
                doc = docx.Document(text_file_path)
                self._get_par_page_positions_and_set_content(docx=doc)
                # print(len(self._file_content))
            case _:
                raise UnsupportedFormatError(f'Неподдерживаемое расширение файла: {self._file_path}')
        # print(self._file_content)
        print('\n\nParagraph positions:\n\n')
        print(self._par_positions)
        print('\n\nPage positions:\n\n')
        print(self._page_positions)

    def _get_par_page_positions_and_set_content(self, **kwargs):
        if 'docx' in kwargs:
            document: docx.Document = kwargs['docx']
            content_chunks = []
            current_position: int = 0
            for par in document.paragraphs:
                content_chunks.append(par.text)
                for i in range(len(par.runs)):
                    if 'lastRenderedPageBreak' in par.runs[i]._element.xml:
                        runs_before = par.runs[:i]
                        runs_before_length = 0 if len(runs_before) == 0 else sum(map(lambda run: len(run.text), runs_before))
                        self._page_positions.append(current_position + runs_before_length)
                self._par_positions.append(current_position)
                current_position += len(par.text) + 1
            current_position -= 1  # Удаляем последний символ, т.к. следующая строка с join не добавляет \n в конце
            self._file_content = '\n'.join(content_chunks)
            # print(f'File content length: {len(self._file_content)}, current position: {current_position}, file_content: \n\n{self._file_content[1069:1139]}')

    def set_nav_option(self, option: NavOption):
        self._nav_option = option

    def get_next(self, position: int) -> int:
        """Возвращает позицию начала следующей опции навигации
        (параграфа или страницы) в тексте после position"""
        match self._nav_option:
            case NavOption.PARAGRAPH:
                return self._get_next_par_position(position)
            case NavOption.PAGE:
                return self._get_next_page_position(position)

    def _get_next_par_position(self, position: int):
        match self._extension:
            case '.docx':
                for par_pos in self._par_positions:
                    if par_pos > position:
                        return par_pos
                return -1

    def _get_next_page_position(self, position: int):
        match self._extension:
            case '.docx':
                for page_pos in self._page_positions:
                    if page_pos > position:
                        return page_pos
                return -1


def test_navigator(file_path: str):
    start_time = time.time()
    navigator = TextNavigator(file_path)
    print(navigator.get_next(1069))
    navigator.set_nav_option(NavOption.PAGE)
    print(navigator.get_next(1069))
    end_time = time.time()
    print(f'Total time: {(end_time - start_time)}')


test_navigator(os.path.abspath('test_files/docx.docx'))
