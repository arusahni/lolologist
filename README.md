lolologist
==========

A python-based tool that generates an image macro from your webcam whenever you commit to a git repository. Inspired by [lolcommits](https://github.com/mroth/lolcommits).

Disclaimer
----------
Still working on packaging. Use at your own risk.

Installing
------------
*BEFORE* installing lolologist, make sure that the following packages are installed locally:

* python-dev
* libfreetype6-dev
* libjpeg-dev

If pillow is already installed and you do not have the packages above, you need to uninstall it and install those packages. This is because when pillow is installed, it compiles optional features based on the availability of those packages. You would do this with commands:

    sudo pip uninstall pillow
    sudo apt-get install python-dev libfreetype6-dev libjpeg-dev

In order to use lolologist, you must also install the following packages:
* mplayer

To install lolologist, after confirming that the above prerequisites are installed, run `sudo python setup.py install`

Using
-----
1. Within the root of your git repository, type `lolologist register`. This should add a githook that will trigger the program every time you commit.
2. Commit!

The path your photo will be printed in the commit output.  Right now, this is `~/.lolologist/{project name}/{10-char sha1}.jpg`. I plan on making it configurable, though.