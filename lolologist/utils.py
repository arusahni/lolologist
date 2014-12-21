#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# pylint: disable=I0011

"""
lolologist utils - helper module for lolologist

    Aru Sahni <arusahni@gmail.com>
"""

from __future__ import unicode_literals, print_function
import os.path
import requests

class LolologistError(Exception):
    """ Custom error type """
    pass

def upload(url, path):
    """ POSTs the file at the given path to the specified endpoint. """
    try:
        image = open(path, 'rb')
        req = requests.post(url, files={'file': (os.path.basename(path), image)})
        if req.status_code != 200:
            raise LolologistError("Couldn't upload the file: {} - {}".format(req.status_code, req.text))
        return req.json().get("data").get("img_url")
    except IOError as e:
        raise LolologistError("Couldn't open the file '{}': {}".format(path, str(e)))
    except requests.exceptions.ConnectionError as e:
        raise LolologistError("Couldn't connect to the host. {}".format(str(e)))
    except requests.exceptions.HTTPError as e:
        raise LolologistError("There was an HTTP error. {}".format(str(e)))
    except requests.exceptions.URLRequired:
        raise LolologistError("The URL '{}' is invalid.".format(url))
    except requests.exceptions.TooManyRedirects as e:
        raise LolologistError("Too many redirects. {}".format(str(e)))
    except AttributeError:
        raise LolologistError("The response data is incorrectly formed.")
