import os
import time

from text_navigator import TextNavigator


def navigator_test(file_path: str):
    start_time = time.time()
    navigator = TextNavigator(file_path)
    # print(navigator.get_next_fragment(1609))
    # navigator.set_nav_option(NavOption.PAGE)
    # print(navigator.get_next_fragment(77))
    end_time = time.time()
    print(f'Total time: {(end_time - start_time)}')


navigator_test(os.path.abspath('test_files/docx.docx'))
