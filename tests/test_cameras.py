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

    def test_capture(self):
        c = Camera(1)
        with pytest.raises(NotImplementedError):
            c._capture()

    @mock.patch("os.makedirs")
    def test_setup(self, makedirs_function):
        assert not makedirs_function.called
        c = Camera(1)
        c._setup()
        assert makedirs_function.called
        assert makedirs_function.call_args_list[0][0][0] == c._output_directory

    @mock.patch("lolologist.cameras.rmtree")
    @mock.patch("os.path.exists")
    def test_cleanup(self, pathexists_function, rmtree_function):
        assert not pathexists_function.called
        assert not rmtree_function.called
        c = Camera(1)
        c._cleanup()
        assert pathexists_function.called
        assert rmtree_function.called
        assert pathexists_function.call_args_list[0][0][0] == c._output_directory
        assert pathexists_function.call_args_list[0][0][0] == c._output_directory


