import stat
import sys

import pytest
import mock

from lolologist.repository import GitRepository
from lolologist.utils import LolologistError

BUILTIN_OPEN = "__builtin__.open" if sys.version_info < (3,) else "builtins.open"

ROOT_PATH = '/'
TEST_HOOK_TEXT = "lorem ipsum"

class MockRepo(object):
    def __init__(self, root_path):
        self.root_path = root_path
        self.git_dir = root_path + '/.git'

def test_init_bad_repository():
    with pytest.raises(LolologistError) as err:
        GitRepository(ROOT_PATH)
    assert 'must contain a valid git repository' in err.exconly()

def test_init_bad_path():
    with pytest.raises(LolologistError) as err:
        GitRepository("BAD PATH")
    assert 'is invalid' in err.exconly()

@mock.patch("git.Repo", return_value=MockRepo(ROOT_PATH))
@mock.patch("lolologist.repository.GitRepository._add_hook")
def test_register(hook_function, repo_function):
    repo = GitRepository(ROOT_PATH)
    repo.register(TEST_HOOK_TEXT)
    assert hook_function.call_args[0][0] == repo_function.return_value.git_dir
    assert hook_function.call_args[0][1] == TEST_HOOK_TEXT

@mock.patch("git.Repo", return_value=MockRepo(ROOT_PATH))
@mock.patch(BUILTIN_OPEN, return_value=mock.MagicMock())
@mock.patch("os.chmod")
@mock.patch("os.stat", return_value=mock.Mock(st_mode=stat.S_IFREG))
@mock.patch("os.path.isfile", return_value=False)
@mock.patch("os.path.join", return_value=ROOT_PATH + ".git/hooks/post-commit")
def test_add_hook(join_f, isfile_f, stat_f, chmod_f, open_f, repo_f):
    repo = GitRepository(ROOT_PATH)
    with mock.patch.object(repo, "_GitRepository__get_hooks_dir",
                           return_value=ROOT_PATH + '.git/hooks') as hooks_function:
        repo.register(TEST_HOOK_TEXT)
        assert join_f.call_args[0][0] == hooks_function.return_value
        assert join_f.call_args[0][1] == 'post-commit'
        assert open_f.call_args[0][0] == join_f.return_value
        assert open_f.call_args[0][1] == 'w'
        assert open_f.return_value.mock_calls[1][1][0] == TEST_HOOK_TEXT
        assert stat_f.call_args[0][0] == join_f.return_value
        assert chmod_f.call_args[0][0] == join_f.return_value
        assert chmod_f.call_args[0][1] ^ stat.S_IFREG == stat.S_IEXEC
