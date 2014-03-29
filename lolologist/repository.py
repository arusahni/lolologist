# -*- coding: utf-8 -*-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
Repository handlers for lolologist.

    Aru Sahni <arusahni@gmail.com>
"""
from __future__ import unicode_literals, print_function

from datetime import datetime
import git
import os
import os.path
import stat

from utils import LolologistError

class GitRepository(object):
    """ A git repository """

    def __init__(self, repository):
        try:
            self.repo = git.Repo(repository)
        except git.InvalidGitRepositoryError:
            raise LolologistError("The path '{}' must contain a valid git repository.".format(repository))

    def register(self, hook_text):
        """ Registers the githooks """
        hooks_dir = os.path.join(self.repo.git_dir, 'hooks')
        if not os.path.isdir(hooks_dir):
            os.makedirs(hooks_dir)

        hook_file = os.path.join(hooks_dir, 'post-commit')
        if os.path.isfile(hook_file): #TODO: Handle multiple post-commit events in the future
            raise LolologistError("There is already a post-commit hook registered for this repository.")

        with open(hook_file, 'w') as script:
            script.write(hook_text)

        hook_perms = os.stat(hook_file)
        os.chmod(hook_file, hook_perms.st_mode | stat.S_IEXEC)
        return True


    def deregister(self):
        """ Removes the commit hook from the repository. """
        hooks_dir = os.path.join(self.repo.git_dir, 'hooks')
        hook_file = os.path.join(hooks_dir, 'post-commit')
        if not os.path.isdir(hooks_dir) or not os.path.isfile(hook_file):
            raise LolologistError("lolologist does not appear to be registered with this repository.")

        os.remove(hook_file) #TODO: ensure this is actually lolologist's


    def get_newest_commit(self, translator=None):
        """ Gets the latest commit in the repository, with an optional formatter for free text areas. """
        if not translator:
            translator = lambda x: x
        head_ref = self.repo.head.reference.commit
        return {
            "project" : os.path.basename(self.repo.working_dir),
            "revision" : head_ref.hexsha[0:10],
            "summary" : translator(head_ref.summary),
            "message" : translator(head_ref.message),
            "time" : datetime.fromtimestamp(head_ref.committed_date),
        }

