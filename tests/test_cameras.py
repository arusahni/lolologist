import pytest
import mock

from lolologist.cameras import Camera, MplayerCamera, ImageSnapCamera

class TestBaseCamera(object):
    """Tests the base camera object functionality"""

    def test_init_warmup(self):
        c = Camera(1)
        assert c._warmup_time == 1

        c = Camera(10)
        assert c._warmup_time == 10

    def test_init_output_dir(self):
        c = Camera(1)
        assert len(c._output_directory) > 0

        c = Camera(1, '/tmp/testdir')
        assert c._output_directory == '/tmp/testdir'

    def test_init_device(self):
        c = Camera(1)
        assert c._device == None

    def test_setup(self):
        c = Camera(1)

