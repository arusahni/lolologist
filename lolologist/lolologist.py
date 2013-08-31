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

import argparse, os, textwrap, git, sys
from PIL import Image, ImageFont, ImageDraw
from subprocess import call, STDOUT
from contextlib import contextmanager
from shutil import rmtree

try:
    from subprocess import DEVNULL
except ImportError:
    DEVNULL = open(os.devnull, 'wb')

MAX_LINES = 3
STROKE_COLOR = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)

POST_COMMIT_FILE = """#!/bin/sh
lolologist capture
"""

class CameraSnapper(object): #pylint: disable=R0903
    """ A picture source """
    def __init__(self, warm_up_time=7, directory='/tmp/lolologist/'):
        """ Initializes a new webcam instance """
        self.temp_directory = directory
        self.frame_offset = warm_up_time


    @contextmanager
    def capture_photo(self):
        """ Captures a photo and provides it for further processing. """
        try:
            call(['mplayer', 'tv://', '-vo', 'jpeg:outdir={}'.format(self.temp_directory), '-frames',
                str(self.frame_offset)], stdout=DEVNULL, stderr=STDOUT)
            yield os.path.join(self.temp_directory, '{0:08d}.jpg'.format(self.frame_offset))
        finally:
            if os.path.exists(self.temp_directory):
                rmtree(self.temp_directory)


class ImageMacro(object):
    """ An image macro """
    def __init__(self, image, top, bottom, font='impact.ttf'):
        """ Initializes the macro with a base image, two lines of text and an optional font """
        self.font = os.path.join(os.path.dirname(__file__), font)
        self.top_text = top
        self.bottom_text = textwrap.wrap(bottom, 30)
        if len(self.bottom_text) > MAX_LINES:
            self.bottom_text[MAX_LINES - 1] = self.bottom_text[MAX_LINES - 1] + '\u2026' #pylint: disable=W1402
        self.image_path = image
        self.size = (0, 0)

    def render(self, target_path='macro.jpg'):
        """ Renders the macro and writes it out to the target path. """
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
        
        image.save(target_path)
        return target_path


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



def make_macro(sha="", message=""):
    """ Creates an image macro with the given text. """
    camera = CameraSnapper()
    with camera.capture_photo() as photo:
        macro = ImageMacro(photo, sha, message)
        print(macro.render())


def get_newest_commit(repo_path='.'):
    """ Retrieves the data for the most recent commit. """
    repo = git.Repo(repo_path)
    head_ref = repo.head.reference.commit
    return {
        "revision" : head_ref.hexsha[0:10],
        "summary" : head_ref.summary,
        "message" : head_ref.message
    }


def capture(args): #pylint: disable=W0613
    """ Capture the most recent commit and macro it! """
    commit = get_newest_commit('.') #always capturing the current repository
    make_macro(commit['revision'], commit['summary'])


def register(args):
    """ Register lolologist with a git repo. """
    print("Attempting to register with the repository '{}'".format(args.repository))
    if not os.path.isdir(os.path.join(args.repository, '.git')):
        raise Exception("The path '{}' must contain a valid git repository".format(args.repository))
    
    hooks_dir = os.path.join(args.repository, '.git', 'hooks')
    if not os.path.isdir(hooks_dir):
        os.makedirs(hooks_dir)

    hook_file = os.path.join(hooks_dir, 'post-commit')
    if os.path.isfile(hook_file): #TODO: Handle multiple post-commit events in the future
        raise Exception("There is already a post-commit hook registered for this repository.")

    with open(hook_file, 'w') as script:
        script.write(POST_COMMIT_FILE)

    os.chmod(hook_file, 755)
    print("Post-commit event successfully registered. Now, get commitin'!")


def deregister(args):
    """ Remove lolologist from a git repo. """
    print("Attempting to deregister from the repository '{}'".format(args.repository))
    if not os.path.isdir(os.path.join(args.repository, '.git')):
        raise Exception("The path '{}' must contain a valid git repository".format(args.repository))
    
    hooks_dir = os.path.join(args.repository, '.git', 'hooks')
    hook_file = os.path.join(hooks_dir, 'post-commit')
    if not os.path.isdir(hooks_dir) or not os.path.isfile(hook_file):
        raise Exception("lolologist does not appear to be registered with this repository.")

    os.remove(hook_file) #TODO: Ensure this is actually lolologist's
    print("Post-commit event successfully deregistered. I haz a sad.")
    

def main():
    """ Entry point for the application """
    parser = argparse.ArgumentParser(description="Document your work in style!")
    subparsers = parser.add_subparsers(title="action commands")

    capture_parser = subparsers.add_parser('capture', help="Capture a snapshot and apply the most recent commit")
    capture_parser.set_defaults(func=capture)

    register_parser = subparsers.add_parser('register', help="Register lolologist with a git repository")
    register_parser.add_argument('repository', nargs='?', default='.', help="The repository to register")
    register_parser.set_defaults(func=register)

    deregister_parser = subparsers.add_parser('deregister', help="Deregister lolologist from a git repository")
    deregister_parser.add_argument('repository', nargs='?', default='.', help="The repository to deregister")
    deregister_parser.set_defaults(func=deregister)

    args = parser.parse_args()

    try:
        args.func(args)
    except Exception as exc:
        print("ERROR: {}".format(exc.message), file=sys.stderr)


if __name__ == '__main__':
    main()
    
