from __future__ import unicode_literals

import pytest
import mock

from lolologist.lolologist import ImageMacro

SAMPLE_PATH = '/sample/path.jpg'
TOP_TEXT = 'This is top text'
BOTTOM_SHORT_TEXT = 'This is bottom text'
BOTTOM_WRAP_TEXT_0 = 'This is some text that should'
BOTTOM_WRAP_TEXT_1 = 'wrap to a subsequent text line'
BOTTOM_WRAP_TEXT_2 = 'unless it is too long to display'

class TestImageMacro(object):

    @mock.patch('os.path.dirname', return_value='/dir/')
    def test_init_basic(self, dirname_function):
        macro = ImageMacro(SAMPLE_PATH, TOP_TEXT, BOTTOM_SHORT_TEXT, 'font.ttf')
        assert macro.font == '/dir/font.ttf'
        assert macro.top_text == TOP_TEXT
        assert isinstance(macro.bottom_text, list)
        assert macro.bottom_text[0] == 'This is bottom text'
        assert macro.size == (0, 0)

    def test_bottom_wrapping(self):
        macro = ImageMacro(SAMPLE_PATH, TOP_TEXT, ' '.join([BOTTOM_WRAP_TEXT_0, BOTTOM_WRAP_TEXT_1]), 'font.ttf')
        assert isinstance(macro.bottom_text, list)
        assert macro.bottom_text[0] == BOTTOM_WRAP_TEXT_0
        assert macro.bottom_text[1] == BOTTOM_WRAP_TEXT_1

    def test_bottom_wrapping_max(self):
        macro = ImageMacro(SAMPLE_PATH, TOP_TEXT, ' '.join([BOTTOM_WRAP_TEXT_0, BOTTOM_WRAP_TEXT_1, BOTTOM_WRAP_TEXT_2]), 'font.ttf')
        assert isinstance(macro.bottom_text, list)
        assert macro.bottom_text[0] == BOTTOM_WRAP_TEXT_0
        assert macro.bottom_text[1] == BOTTOM_WRAP_TEXT_1
        assert macro.bottom_text[2] != BOTTOM_WRAP_TEXT_2
        assert macro.bottom_text[2][:24] == BOTTOM_WRAP_TEXT_2[:24]
        assert macro.bottom_text[2][24] == '\u2026' #ellipses


