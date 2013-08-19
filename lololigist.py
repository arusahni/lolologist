#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import unicode_literals, print_function

import argparse, os
from PIL import Image
from subprocess import call, STDOUT
from contextlib import contextmanager
from shutil import rmtree

try:
	from subprocess import DEVNULL
except ImportError:
	DEVNULL = open(os.devnull, 'wb')

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
			call(['mplayer', '-vo', 'jpeg:outdir={}'.format(self.temp_directory),'-frames', 
				str(self.frame_offset), 'tv://'], stdout=DEVNULL, stderr=STDOUT)
			yield os.path.join(self.temp_directory, '{0:08d}.jpg'.format(self.frame_offset))
		finally:
			if os.path.exists(self.temp_directory):
				rmtree(self.temp_directory)


class GitCommit(object):
	def __init__(self, revision, message):
		self.revision = revision
		self.message = message


def get_picture():
	camera = CameraSnapper()
	with camera.capture_photo() as photo:
		image = Image.open(photo)
		image.save('photo.jpg')
		print(photo)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Document your work in style!")
	parser.add_argument('-c, --capture', nargs=argparse.REMAINDER)
	parser.add_argument('--test', action='store_true')
	
	args = parser.parse_args();

	if args.test:
		print('Test!')
		get_picture()