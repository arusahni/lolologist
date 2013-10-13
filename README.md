lolologist
==========

A python-based tool that generates an image macro from your webcam whenever you commit to a git repository. Inspired by [lolcommits](https://github.com/mroth/lolcommits).

Installing
------------
*BEFORE* installing lolologist, make sure that the following packages are installed locally:

* python-dev
* libfreetype6-dev
* libjpeg-dev

If pillow is already installed and you do not have the packages above, you need to uninstall it and install those packages. This is because when pillow is installed, it compiles optional features based on the availability of those packages. You would do this with commands:

```bash
sudo pip uninstall pillow
sudo apt-get install python-dev libfreetype6-dev libjpeg-dev

# Optional, for a better font
sudo apt-get install ttf-mscorefonts-installer
```
In order to use lolologist, you must also install the following packages:
* mplayer

To install lolologist, after confirming that the above prerequisites are installed, run `sudo python setup.py install`

**Note**: This library is not yet compatible with Pillow 2.2.0 and above due to an unannounced change to how they draw fonts. Apparently things will be fixed/standardized in their 2.3.0 release, but for now I'm forcing the version number.

Using
-----
1. Within the root of your git repository, type `lolologist register`. This should add a githook that will trigger the program every time you commit.
2. Commit!

The path to your photo will be printed in the commit output.  To configure this, please edit the `~/.lolologistrc` file.  Pythonic format strings are accepted, with the caveat that *percent signs have to be escaped with another percent sign*.

For example, if you wanted to group images by the commit year and month, you could use the following:

```ini
OutputDirectory = ~/.lolologist/{project}/{time:%%Y}/{time:%%m}
```

Possible substition parameters:

| Parameter  | Type       | Description                                |
| ---------- | :--------: | ------------------------------------------ |
| `project`  | *string*   | The name of the git repository's directory |
| `revision` | *string*   | A ten character ref sha                    |
| `message`  | *string*   | The entire commit message.                 |
| `time`     | *datetime* | The time of the commit.                    |

Fonts
-----
Due to licensing concerns, I can't distribute lolologist with the iconic Impact TrueType font.  To account for this, lolologist will use your system's Impact if it exists, or fall back to an open font.

If Impact isn't installed on your system, [download and install it](http://www.cufonfonts.com/en/font/12047/impact), and then run either `lolologist setfont` or `lolologist setfont <path-to-font>` to load it.