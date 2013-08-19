#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import unicode_literals, print_function

import argparse, os, textwrap
from PIL import Image, ImageFont, ImageDraw
from subprocess import call, STDOUT
from contextlib import contextmanager
from shutil import rmtree

try:
	from subprocess import DEVNULL
except ImportError:
	DEVNULL = open(os.devnull, 'wb')

MAX_LINES = 3
STROKE_COLOR = (0,0,0)
TEXT_COLOR = (255, 255, 255)

class CameraSnapper(object):
	''' A picture source '''

	def __init__(self, warm_up_time=7, directory='/tmp/lololigist/'):
		''' Initializes a new webcam instance '''
		self.temp_directory = directory
		self.frame_offset = warm_up_time

	@contextmanager
	def capture_photo(self):
		''' Captures a photo and provides it for further processing. '''
		try:
			call(['mplayer', 'tv://', '-vo', 'jpeg:outdir={}'.format(self.temp_directory),'-frames', 
				str(self.frame_offset)], stdout=DEVNULL, stderr=STDOUT)
			yield os.path.join(self.temp_directory, '{0:08d}.jpg'.format(self.frame_offset))
		finally:
			if os.path.exists(self.temp_directory):
				rmtree(self.temp_directory)


class GitCommit(object):
	def __init__(self, revision, message):
		self.revision = revision
		self.message = message


class ImageMacro(object):
	''' An image macro '''
	def __init__(self, image, top, bottom, font='impact.ttf'):
		self.font = font
		self.top_text = top
		self.bottom_text = textwrap.wrap(bottom, 30)
		if len(self.bottom_text) > MAX_LINES:
			self.bottom_text[MAX_LINES - 1] = self.bottom_text[MAX_LINES - 1] + '\u2026'
		self.image_path = image


	def render(self, target_path=None):
		image = Image.open(self.image_path)
		self.size = image.size
		top_font_size = 32
		bottom_font_size = 48

		top_dimensions = self.__get_text_dimensions(self.top_text, top_font_size)
		top_position = (self.size[0] - 5 - top_dimensions[0], 5)

		draw = ImageDraw.Draw(image)
		self.__draw_image(draw, self.top_text, top_font_size, top_position)
		
		lines = min(len(self.bottom_text), MAX_LINES)
		print(lines)
		for row in range(lines):
			bottom_offset = ((lines - 1 - row) * bottom_font_size) + 5
			bottom_dimensions = self.__get_text_dimensions(self.bottom_text[row], bottom_font_size)
			bottom_position = (self.size[0]/2 - bottom_dimensions[0]/2,
								self.size[1] - bottom_offset - bottom_dimensions[1])

			self.__draw_image(draw, self.bottom_text[row], bottom_font_size, bottom_position)
		
		image.save('macro.jpg')
		return 'macro.jpg'


	def __draw_image(self, draw, text, font_size, position, stroke_width=3): #, bottom_font_size, bottom_dimensions, stroke_width=3):
		font = ImageFont.truetype(self.font, font_size)
		for x in range(-stroke_width, stroke_width + 1):
			for y in range(-stroke_width, stroke_width + 1):
				draw.text((position[0] + x, position[1] + y), text, STROKE_COLOR, font=font)
		draw.text(position, text, TEXT_COLOR, font=font)



	def __get_text_dimensions(self, text, font_size):
		font = ImageFont.truetype(self.font, font_size)
		return font.getsize(text)



def get_picture(sha="xxxxxxxx", text="This is some really long text. Just how long will it get? I have nooooo idea. Or do I? Who knows. Only The Shadow."):
	camera = CameraSnapper()
	with camera.capture_photo() as photo:
		macro = ImageMacro(photo, sha, text)
		print(macro.render())


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Document your work in style!")
	parser.add_argument('-c, --capture', nargs=argparse.REMAINDER)
	parser.add_argument('--test', action='store_true')
	
	args = parser.parse_args();

	if args.test:
		print('Test!')
		get_picture()