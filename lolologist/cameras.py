# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# pylint: disable=I0011

""" 
Camera interfaces for lolologist.

    Aru Sahni <arusahni@gmail.com>
"""

from __future__ import unicode_literals

from contextlib import contextmanager
import os
import os.path
from shutil import rmtree
from subprocess import call, STDOUT

try:
    from subprocess import DEVNULL # pylint disable=no-name-in-module
except ImportError:
    DEVNULL = open(os.devnull, 'wb')

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

