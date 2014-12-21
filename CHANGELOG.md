Releases
========

v0.4.0 - 2014-06-01
-------------------
Oh hi, I didn't see you there.

### Notes
No submodule support as originally promised due to issues with the GitPython library. Will implement when their implementation is compatible with newer Git repo versions.

### Enhancements
* Removed explicit Pillow version declaration. (#17)
* Commit messages can now be translated into lolspeak.
* Images can be uploaded after generation (#15)
* OS X support w/imagesnap library (#18)

### Bugfixes
* Images are now scaled down to ~640x480 for consistency across hardware (#19)

v0.3.1 - 2013-10-13
-------------------

### Bugfixes
* Specifying a Pillow version to avoid hitting a library font sizing bug.

v0.3.0 - 2013-09-09
-------------------

### Notes
* No longer packaging Impact, and instead using LeaguGothicRegular in order to not offend the copyright gods.

### Enhancements
* User-definable fonts. (#12)

### Bugfixes
* Better repository registration handling.

v0.2.0 - 2013-09-07
-----------------
First release!