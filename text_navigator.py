import os.path
import re
from typing import List, Optional, Tuple
from zipfile import ZipFile
import shutil

import docx
import pymupdf

from exceptions import *
from general import NavOption, try_open_txt, LINE_LENGTH_MAX, LINES_ON_HTML_PAGE


class TextNavigator:
    _nav_option: NavOption  # Опция навигации - страница или абзац
    _file_path: str  # Путь к текстовому файлу
    _file_content: str  # Содержимое файла
    _extension: str  # Расширение файла
    _par_positions: List[int]  # Позиции параграфов
    _page_positions: List[int]  # Позиции страниц
    _encoding: Optional[str]  # Актуально для txt файла как доп опция получения кодировки

    def __init__(self, text_file_path: str):
        self._encoding = None
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
            case '.doc':
                self._set_doc_content()
            case '.pdf' | '.epub' | '.fb2':
                self._set_pypdf_content()
            case '.htm' | '.html':
                self._set_html_content()
            case '.xml':
                self._set_xml_content()
            case '.odt':
                self._set_odt_content()
            case '.rtf':
                self._set_rtf_content()
            case '.txt':
                self._set_txt_content()
            case _:
                raise UnsupportedFormatError(f'Неподдерживаемое расширение файла: {self._file_path}')
        print(self._file_content[19366:19738])
        # print('\n\nParagraph positions:\n\n')
        # print(self._par_positions)
        # print('\n\nPage positions:\n\n')
        # print(self._page_positions)
        print(f'\n\nFile content with one page: {self._file_content[19390:19517]}')

    # INFO: private methods

    def _set_positions(self, chunks: List[str]):
        start_position = 0
        lines_count = 0
        self._par_positions.append(start_position)
        self._page_positions.append(start_position)
        for par in chunks:
            par_length = len(par)
            # Добавляем позиции абзацев
            start_position += par_length + 1
            self._par_positions.append(start_position)
            # Добавляем позиции страниц
            par_lines = 1 + par_length // LINE_LENGTH_MAX  # Количество строк, занимаемое абзацем
            if (lines_count + par_lines) == LINES_ON_HTML_PAGE:
                self._page_positions.append(start_position)
                lines_count = 0
            elif (lines_count + par_lines) > LINES_ON_HTML_PAGE:
                self._page_positions.append(start_position - par_length)
                lines_count = par_lines
            else:
                lines_count += par_lines

    # INFO: setting content for different formats block

    def _set_txt_content(self):
        content, encoding = try_open_txt(self._file_path)
        self._encoding = encoding
        self._file_content = re.sub(r'\n{2,}', '\n', content.strip())
        content_chunks = self._file_content.split('\n')
        self._set_positions(content_chunks)

    def _set_rtf_content(self):
        from striprtf.striprtf import rtf_to_text
        with open(self._file_path, 'r') as file:
            content = file.read()
        content = rtf_to_text(content)
        self._file_content = re.sub(r'\n{2,}', '\n', content.strip())
        content_chunks = self._file_content.split('\n')
        self._set_positions(content_chunks)

    def _set_doc_content(self):
        import subprocess

        result = subprocess.run(['antiword', self._file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        content = result.stdout.decode()

        # INFO: здесь будет пока тестовый текст, т.к. для проверки на Windows проблематично установить antiword
        self._file_content = content
        content_chunks = content.split('\n')
        self._set_positions(content_chunks)

    def _set_odt_content(self):
        filename, _ = os.path.splitext(self._file_path)
        temp_zip = filename + '.zip'
        shutil.copy(self._file_path, temp_zip)
        try:
            with ZipFile(temp_zip, 'r') as zip_file:
                with zip_file.open('content.xml') as xml_file:
                    xml_content = xml_file.read()
                    content = xml_content.decode('utf-8')
        finally:
            os.remove(temp_zip)
        if not content:
            raise ODTError("Файл content.xml отсутствует в ODT файле")
        # Далее работаем как с xml файлом с особенными тегами
        content_chunks = []
        text_matches = re.finditer(r'>([^<].*?)<', content, re.DOTALL)
        for text_match in text_matches:
            content_chunks.append(text_match.group(1))
        self._file_content = '\n'.join(content_chunks)
        self._set_positions(content_chunks)

    def _set_xml_content(self):
        content, _ = try_open_txt(self._file_path)
        content = re.sub(r'<\?xml.*?>\n', '', content)
        content = re.sub(r'\s{2,}', '\n', content)
        content = re.sub(r'</.*?>', ' ', content)
        tag_matches = re.finditer(r'<([^>].*?)>', content, re.DOTALL)
        for tag_match in tag_matches:
            tag = tag_match.group(1)
            content = content.replace(tag, tag.split(' ')[0])
        content = content.replace('<', '').replace('>', ': ')
        content = re.sub(r'(\n\s*)', '\n', content)
        self._file_content = content
        self._set_positions(self._file_content.split('\n'))

    def _set_html_content(self):
        content, _ = try_open_txt(self._file_path)
        # Удалим все скрипты и стили
        clean_html = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', content, flags=re.DOTALL)

        # Удалим все HTML теги
        plain_text = re.sub(r'<[^>]+>', '', clean_html)

        # Удалим пробелы и переводы строк в начале и в конце строк
        plain_text = plain_text.strip()

        # Заменим большое количество пробелов на знак переноса
        plain_text = re.sub('\s{2,}', '\n', plain_text)

        self._file_content = plain_text

        # Теперь устанавливаем позиции параграфов и страниц.
        # Позиции параграфов легко установить по знаку разделителя
        # \n, который мы добавили.
        # Позиции страниц - виртуальные, по примеру из Word:
        # максимум 120 символов в строке, максимум 52 строки на странице.
        self._set_positions(self._file_content.split('\n'))

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

    def _get_next_fragment(self, position: int) -> Optional[Tuple[int, Optional[int]]]:
        for i in range(len(self._nav_positions)):
            if self._nav_positions[i] > position:
                start_position = self._nav_positions[i]
                if len(self._file_content[start_position:]) == 0:
                    return None  # Вернуть None, если start_position - последняя позиция
                try:
                    end_position = self._nav_positions[i + 1]
                    return start_position, end_position
                except IndexError:
                    return start_position, None  # Гипотетический случай, который, скорее всего, никогда не произойдет :)
        return None

    def _get_prev_fragment(self, position: int) -> Optional[Tuple[int, Optional[int]]]:
        nav_positions_reversed = self._nav_positions[::-1]
        for i in range(len(nav_positions_reversed)):
            if nav_positions_reversed[i] < position:
                start_position = nav_positions_reversed[i]
                try:
                    end_position = self._nav_positions[i - 1]
                    return start_position, end_position
                except IndexError:
                    return start_position, None
        return None

    # INFO: public methods

    def set_nav_option(self, option: NavOption):
        """Установить опцию навигации - на данный момент страница или параграф"""
        self._nav_option = option

    def get_next_fragment(self, position: int) -> Optional[Tuple[int, Optional[int]]]:
        """Возвращает диапазон позиций следующей опции навигации
        (параграфа или страницы) в тексте после position"""
        return self._get_next_fragment(position)

    def get_prev_fragment(self, position: int) -> Optional[Tuple[int, Optional[int]]]:
        """Возвращает диапазон позиций предыдущей опции навигации
        (параграфа или страницы) в тексте после position"""
        return self._get_prev_fragment(position)

    def get_file_content(self) -> str:
        """
        Вспомогательный метод для уверенности, что читаемое содержимое
        и содержимое для поиска позиций навигации созданы единообразно
        """
        return self._file_content

    def get_encoding(self) -> Optional[str]:
        """
        Получение кодировки файла (выполняется попутно с получением
        содержимого файла, не требует затрат). Актуально для txt
        """
        return self._encoding
