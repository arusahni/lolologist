#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# pylint: disable=I0011

"""
lolologist - an automated image macro generator for your commits. Simply tack it onto your
    git repository's commit hook and let 'er rip!

    Aru Sahni <arusahni@gmail.com>
"""

from __future__ import unicode_literals, print_function

import configparser
import argparse, os, textwrap, sys
from PIL import Image, ImageFont, ImageDraw
from subprocess import call, check_output, STDOUT
from contextlib import contextmanager
from shutil import rmtree
from lolz import Tranzlator

from utils import LolologistError, upload
from repository import GitRepository

try:
    from subprocess import DEVNULL
except ImportError:
    DEVNULL = open(os.devnull, 'wb')

MAX_LINES = 3
STROKE_COLOR = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)
FALLBACK_FONT = "LeagueGothic-Regular.otf" # Change in setup.py, too
DEFAULT_UPLOAD_URL = 'http://uploads.im/api?upload'

CURRENT_PLATFORM = 0
PLATFORM_LINUX = 1
PLATFORM_OSX = 2

POST_COMMIT_FILE = """#!/bin/sh
lolologist capture
"""

def detect_platform():
    global CURRENT_PLATFORM
    if sys.platform.startswith("linux"):
        CURRENT_PLATFORM = PLATFORM_LINUX
    elif sys.platform == 'darwin':
        CURRENT_PLATFORM = PLATFORM_OSX
    else:
        print("Unsupported platform detected. Assuming Linux.", file=sys.stderr)
        CURRENT_PLATFORM = PLATFORM_LINUX

def is_linux():
    """Determines if the current platform is Linux
    :returns: @todo

    """
    return CURRENT_PLATFORM == PLATFORM_LINUX

def is_osx():
    """Determines if the current platform is OSX
    
    :returns: @todo

    """
    return CURRENT_PLATFORM == PLATFORM_OSX


class Camera(object):

    """A base camera object"""

    def __init__(self, warmup_time, directory='/tmp/lolologist/'):
        """A base implementation of the webcam, not directly callable

        :param warmup_time: @todo
        :param directory: @todo

        """
        self._warmup_time = warmup_time
        self._output_directory = directory
        
    @contextmanager
    def capture_photo(self):
        """Captures a photo from the camera and provides its path for further processing
        
        :returns: @todo

        """
        try:
            self._setup()
            yield self._capture()
        finally:
            self._cleanup()

    def _capture(self):
        raise NotImplementedError("Override this.")

    def _setup(self):
        os.makedirs(self._output_directory)

    def _cleanup(self):
        """Cleans the camera up after itself like a big boy
        
        :returns: @todo

        """
        if os.path.exists(self._output_directory):
            rmtree(self._output_directory)


class MplayerCamera(Camera): #pylint: disable=R0903
    """ A picture source """
    def __init__(self, warmup_time=7):
        """ Initializes a new webcam instance """
        super(MplayerCamera, self).__init__(warmup_time)

    def _capture(self):
        """ Captures a photo and provides it for further processing. """
        call(['mplayer', 'tv://', '-vo', 'jpeg:outdir={}'.format(self._output_directory), '-frames',
              str(self._warmup_time)], stdout=DEVNULL, stderr=STDOUT)
        return os.path.join(self._output_directory, '{0:08d}.jpg'.format(self._warmup_time)) #get the last captured frame


class ImageSnapCamera(Camera):

    """Uses imagesnap to capture a photo"""

    def __init__(self, warmup_time=1.2):
        """Initializes a new webcam instance

        :param warmup_time: @todo

        """
        super(ImageSnapCamera, self).__init__(warmup_time)
        
    def _capture(self):
        """Captures a photo using imagesnap and provides the path for further processing

        :returns: the full path of the captured image

        """
        outpath = os.path.join(self._output_directory, 'snapshot.jpg')
        call(['imagesnap', '-w', str(self._warmup_time), '-q', outpath], stdout=DEVNULL, stderr=STDOUT)
        return outpath


class ImageMacro(object):
    """ An image macro """
    def __init__(self, image, top, bottom, font):
        """ Initializes the macro with a base image, two lines of text and an optional font """
        self.font = os.path.join(os.path.dirname(__file__), font)
        self.top_text = top
        self.bottom_text = textwrap.wrap(bottom, 30)
        if len(self.bottom_text) > MAX_LINES:
            self.bottom_text[MAX_LINES - 1] = self.bottom_text[MAX_LINES - 1] + '\u2026' #pylint: disable=W1402
        self.image_path = image
        self.size = (0, 0)


    def render(self):
        """ Returns the rendered macro. """
        image = Image.open(self.image_path)
        self.size = image.size
        top_font_size = 32
        bottom_font_size = 48

        top_dimensions = self.__get_text_dimensions(self.top_text, top_font_size)
        top_position = (self.size[0] - 5 - top_dimensions[0], 3)

        draw = ImageDraw.Draw(image)
        self.__draw_image(draw, self.top_text, top_font_size, top_position)

        lines = min(len(self.bottom_text), MAX_LINES)

        for row in range(lines):
            bottom_offset = ((lines - 1 - row) * bottom_font_size) + 15
            bottom_dimensions = self.__get_text_dimensions(self.bottom_text[row], bottom_font_size)
            bottom_position = (self.size[0]/2 - bottom_dimensions[0]/2,
                    self.size[1] - bottom_offset - bottom_dimensions[1])
            self.__draw_image(draw, self.bottom_text[row], bottom_font_size, bottom_position)

        return image


    def __draw_image(self, draw, text, font_size, position, stroke_width=3):
        """ Draws the text with the given attributes to the image. """
        font = ImageFont.truetype(self.font, font_size)
        for x_off in range(-stroke_width, stroke_width + 1):
            for y_off in range(-stroke_width, stroke_width + 1):
                draw.text((position[0] + x_off, position[1] + y_off), text, STROKE_COLOR, font=font)
        draw.text(position, text, TEXT_COLOR, font=font)


    def __get_text_dimensions(self, text, font_size):
        """ Gets the measurements of text rendered at a specific font size. """
        font = ImageFont.truetype(self.font, font_size)
        return font.getsize(text)


class Config(object): #pylint: disable=R0903
    """ Handles configuration creation and access. """
    def __init__(self, section="DEFAULT"):
        """ Creates a configuration object """
        self.config_file = os.path.expanduser('~/.lolologistrc')
        if not os.path.isfile(self.config_file):
            self.__create_config()
        config = configparser.ConfigParser()
        config.read(self.config_file)
        if section not in config:
            self.__section = "DEFAULT"
        else:
            self.__section = section
        self.__parser = config[self.__section]


    def __create_config(self):
        """ Creates the file with acceptable defaults """
        config = configparser.ConfigParser()
        config['DEFAULT'] = {
            "OutputDirectory" : os.path.join(os.path.expanduser('~'), '.lolologist', '{project}'),
            "OutputFileName" : '{revision}',
            "OutputFormat" : 'jpg',
        }

        font_path = get_impact()
        if font_path:
            config['DEFAULT']['FontPath'] = font_path

        with open(self.config_file, 'w') as config_file:
            config.write(config_file)


    def __getitem__(self, field):
        """ Gets the value of a specific field """
        return self.__parser[field]


    def __len__(self):
        """ Required for Lintin'"""
        return len(self.__parser)


    def get_font(self):
        """ Gets the configuration entry for the macro font. """
        font = self.__parser.get('FontPath', FALLBACK_FONT)
        if font == FALLBACK_FONT:
            print("WARNING: No font found. Using fallback. Run `lolologist setfont --help` for more information.")
        return font


    @property
    def lol_speak(self):
        """ Returns `True` if the lolspeak translator is enabled. """
        return self.__parser.getboolean('LolSpeak', False)


    def update_config(self, setting, value):
        """ Sets a value for the specific setting in the DEFAULT section. """
        config = configparser.ConfigParser()
        config.read(self.config_file)
        config["DEFAULT"][setting] = value

        with open(self.config_file, 'w') as config_file:
            config.write(config_file)

        self.__parser = config[self.__section]


    def clear_setting(self, setting):
        """ Removes a setting from the DEFAULT section. """
        config = configparser.ConfigParser()
        config.read(self.config_file)
        config.remove_option('DEFAULT', setting)

        with open(self.config_file, 'w') as config_file:
            config.write(config_file)

        self.__parser = config[self.__section]


    @property
    def upload(self):
        """ Determines if the uploader should be triggered. """
        return self.__parser.getboolean('UploadImages', False) and len(self.upload_url) > 0


    @property
    def upload_url(self):
        """ The URL to upload to. """
        return self.__parser.get('UploadUrl', DEFAULT_UPLOAD_URL)


class Lolologist(object):
    """ The main application """

    def __init__(self, repo_path='.'):
        detect_platform()
        self.config = Config()
        self.repo_path = repo_path


    def __make_macro(self, revision, summary, **kwargs):
        """ Creates an image macro with the given text. """
        # camera = CameraSnapper()
        camera = ImageSnapCamera()
        with camera.capture_photo() as photo:
            macro = ImageMacro(photo, revision, summary, self.config.get_font())
            image = macro.render()
            directory_path = self.config['OutputDirectory'].format(revision=revision, **kwargs)
            if not os.path.isdir(directory_path):
                os.makedirs(directory_path)
            file_path = os.path.join(self.config['OutputDirectory'], self.config['OutputFileName']).format(
                revision=revision,
                **kwargs
            ) + '.' + self.config["OutputFormat"]
            image.save(file_path)
            return file_path


    def __get_newest_commit(self):
        """ Retrieves the data for the most recent commit. """
        loltranz = Tranzlator()
        translator = loltranz.translate_sentence if self.config.lol_speak else None
        return GitRepository(self.repo_path).get_newest_commit(translator=translator)


    def capture(self, args): #pylint: disable=W0613
        """ Capture the most recent commit and macro it! """
        commit = self.__get_newest_commit()
        image = self.__make_macro(**commit)
        if self.config.upload:
            url = upload(self.config.upload_url, image)
            print("Uploaded:", url)
        print("Macro saved:", image)


    @staticmethod
    def register(args): #pylint: disable=W0613
        """ Register lolologist with a git repo. """
        print("Attempting to register with the repository '{}'".format(args.repository))
        GitRepository(args.repository).register(POST_COMMIT_FILE)


    @staticmethod
    def deregister(args): #pylint: disable=W0613
        """ Remove lolologist from a git repo. """
        print("Attempting to deregister from the repository '{}'".format(args.repository))
        GitRepository(args.repository).deregister()
        print("Post-commit event successfully deregistered. I haz a sad.")


    def set_font(self, args):
        """ Sets the default image macro font. """
        font_path = args.font_path if args.font_path else get_impact()
        if font_path:
            self.config.update_config("FontPath", font_path)
            print("Font successfully set to '{}'".format(font_path))
        else:
            raise LolologistError("Could not find Impact. Falling back to League Gothic.")


    def speak_lolz(self, args):
        """ Sets the state of lolspeak for commits """
        enabled = args.lol_on.lower() == "on" if args.lol_on else False
        if (not self.config.lol_speak and args.lol_on.lower() == "on") or \
                (self.config.lol_speak and args.lol_on.lower() == "off"):
            self.config.update_config("LolSpeak", args.lol_on.lower())
        print("Lolspeak {}!".format("enabled" if enabled else "disabled"))


    def set_uploader(self, args):
        """ Sets the state of the uploader, as well as the URL endpoint."""
        action = args.action.lower()
        if action == "on" or action == "off":
            self.config.update_config("UploadImages", action)
        if action == "clear":
            self.config.clear_setting("UploadUrl")
        elif args.url:
            self.config.update_config("UploadUrl", args.url)


def get_impact_locations():
    """ Gets the location of the Impact font for the current operating system
    """
    if is_osx():
        return check_output(['locate', '-i', 'Impact.ttf'], stderr=STDOUT)
    return check_output(['locate', '--regex', '-i', 'Impact.ttf$'], stderr=STDOUT)

def get_impact():
    """ Finds Impact.ttf on one's system and returns the best path for it. """
    locs = get_impact_locations()
    font_path = None
    for loc in locs.splitlines():
        if loc.startswith("/usr") or loc.startswith('/Library'): #most likely a permanent font
            font_path = loc
            break
        elif font_path is None:
            font_path = loc
    return font_path

def main():
    """ Entry point for the application """
    app = Lolologist()
    parser = argparse.ArgumentParser(description="Document your work in style!")
    subparsers = parser.add_subparsers(title="action commands")

    capture_parser = subparsers.add_parser('capture', help="Capture a snapshot and apply the most recent commit")
    capture_parser.set_defaults(func=app.capture)

    register_parser = subparsers.add_parser('register', help="Register lolologist with a git repository")
    register_parser.add_argument('repository', nargs='?', default='.', help="The repository to register")
    register_parser.set_defaults(func=Lolologist.register)

    deregister_parser = subparsers.add_parser('deregister', help="Deregister lolologist from a git repository")
    deregister_parser.add_argument('repository', nargs='?', default='.', help="The repository to deregister")
    deregister_parser.set_defaults(func=Lolologist.deregister)

    setfont_parser = subparsers.add_parser('setfont', help="Set the font to use for image macros.")
    setfont_parser.add_argument('font_path', nargs="?",
        help="The full path to the desired font. If none is specified, attempt to find the system's Impact font."
    )
    setfont_parser.set_defaults(func=app.set_font)

    tranzlator_parser = subparsers.add_parser('speaklolz', help="Translate commit summaries and messages to lolzspeak.")
    tranzlator_parser.add_argument('lol_on', help="'on' to enable the translator, 'off' to disable it.")
    tranzlator_parser.set_defaults(func=app.speak_lolz)

    uploader_parser = subparsers.add_parser('uploader', help="Set file uploading preferences.")
    uploader_parser.add_argument('action', choices=['on', 'off', 'set', 'clear'], help="'on' to enable the uploader, 'off' to disable it, 'set' to set the url, 'clear' to clear the URL.")
    uploader_parser.add_argument('url', nargs='?', default=None, help="The URL to POST the image to.")
    uploader_parser.set_defaults(func=app.set_uploader)

    args = parser.parse_args()
    try:
        args.func(args)
    except LolologistError as exc:
        print("ERROR: {}".format(exc.message), file=sys.stderr)


if __name__ == '__main__':
    main()
