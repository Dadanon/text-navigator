import re
from enum import IntEnum
from zipfile import ZipFile
from xml.etree import ElementTree as ET
import docx


class NavOption(IntEnum):
    PARAGRAPH = 0
    PAGE = 1


SUPPORTED_FORMATS = [
    'txt',
    'rtf',
    'doc',
    'docx',
    'odt',
    'htm',
    'html',
    'xml',
    'pdf',
    'fb2',
    'epub'
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


def read_docx(file_name):
    with ZipFile(file_name) as docx:
        with docx.open('word/document.xml') as xml_file:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            paragraphs = []

            for paragraph in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
                text = ''.join(node.text for node in paragraph.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'))
                paragraphs.append(text)

            return '\n'.join(paragraphs)


def read_python_docx(file_name):
    doc = docx.Document(file_name)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    return '\n'.join(fullText)


def read_pdf(file_name):
    # Extract text from PDF using PyPDF2 (still requires an external library)
    import PyPDF2
    reader = PyPDF2.PdfFileReader(file_name)
    text = []
    for i in range(reader.numPages):
        page = reader.getPage(i)
        text.append(page.extractText())
    return '\n'.join(text)


def read_epub(file_name):
    # Extract text from EPUB by parsing the EPUB structure
    with ZipFile(file_name) as epub:
        text = []
        for file_info in epub.infolist():
            if file_info.filename.endswith('.xhtml') or file_info.filename.endswith('.html'):
                with epub.open(file_info) as html_file:
                    html_content = html_file.read().decode('utf-8')
                    text.append(re.sub('<[^<]+?>', '', html_content))  # Remove HTML tags
        return '\n'.join(text)


def read_html_xml(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        text = file.read()
        return re.sub('<[^<]+?>', '', text)
