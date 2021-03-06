import sys

import pytest
import mock

from lolologist.utils import upload, LolologistError

TEST_URL = "http://test/url"
TEST_PATH = "/test/path.jpg"
TEST_PATH_BASENAME = "path.jpg"

BUILTIN_OPEN = "__builtin__.open" if sys.version_info < (3,) else "builtins.open"

class MockResponse(object):
    """ A fake requests response """
    def __init__(self, status_code=200, text=""):
        self.status_code = status_code
        self.text = text

    def json(self):
        """ Gets the response JSON """
        return {"data": {"img_url": TEST_URL + "/" + TEST_PATH_BASENAME}}

@mock.patch("requests.post")
@mock.patch("os.path.basename")
@mock.patch(BUILTIN_OPEN)
def test_upload_image_open(open_function, basename_function, post_function):
    with pytest.raises(LolologistError) as err:
        upload(TEST_URL, TEST_PATH)
    assert open_function.call_args_list[0][0][0] == TEST_PATH
    assert open_function.call_args_list[0][0][1] == "rb"
    assert "Couldn't upload the file" in err.exconly()

@mock.patch("requests.post")
@mock.patch("os.path.basename")
@mock.patch(BUILTIN_OPEN)
def test_upload_basename(open_function, basename_function, post_function):
    with pytest.raises(LolologistError) as err:
        upload(TEST_URL, TEST_PATH)
    assert basename_function.call_args_list[0][0][0] == TEST_PATH
    assert "Couldn't upload the file" in err.exconly()

@mock.patch("requests.post")
@mock.patch(BUILTIN_OPEN, return_value="opened image")
def test_upload_post_payload(open_function, post_function):
    with pytest.raises(LolologistError) as err:
        upload(TEST_URL, TEST_PATH)
    _, kwargs = post_function.call_args_list[0]
    assert 'files' in kwargs
    assert 'file' in kwargs['files']
    assert kwargs['files']['file'][0] == TEST_PATH_BASENAME
    assert kwargs['files']['file'][1] == "opened image"
    assert "Couldn't upload the file" in err.exconly()

@mock.patch("requests.post")
@mock.patch("os.path.basename")
@mock.patch(BUILTIN_OPEN, return_value="opened image")
def test_upload_post_url(open_function, basename_function, post_function):
    with pytest.raises(LolologistError) as err:
        upload(TEST_URL, TEST_PATH)
    assert post_function.call_args_list[0][0][0] == TEST_URL
    assert "Couldn't upload the file" in err.exconly()

@mock.patch("requests.post", return_value=MockResponse(status_code=200))
@mock.patch("os.path.basename")
@mock.patch(BUILTIN_OPEN, return_value="opened image")
def test_upload_success(open_function, basename_function, post_function):
    upload(TEST_URL, TEST_PATH)
    assert post_function.called

@mock.patch("requests.post", return_value=MockResponse(status_code=200))
@mock.patch("os.path.basename")
@mock.patch(BUILTIN_OPEN, return_value="opened image")
def test_upload_success_payload(open_function, basename_function, post_function):
    image_url = upload(TEST_URL, TEST_PATH)
    assert post_function.return_value.json()["data"]["img_url"] == image_url

@mock.patch("requests.post", return_value=MockResponse(status_code=500))
@mock.patch("os.path.basename")
@mock.patch(BUILTIN_OPEN, return_value="opened image")
def test_upload_failure_status(open_function, basename_function, post_function):
    with pytest.raises(LolologistError) as err:
        upload(TEST_URL, TEST_PATH)
    assert post_function.called
    assert "Couldn't upload the file" in err.exconly()
    assert post_function.return_value.status_code == 500
