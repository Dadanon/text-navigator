from enum import IntEnum


class NavOption(IntEnum):
    PARAGRAPH = 0
    PAGE = 1


SUPPORTED_FORMATS = [
    '.doc',
    '.docx',
    '.pdf',
    '.txt'
]
"""Список будет дополняться со временем"""
