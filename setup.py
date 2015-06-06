""" Set it up. """

from __future__ import print_function

from setuptools import setup
import sys

try:
    import pypandoc
    LONG_DESCRIPTION = pypandoc.convert('README.md', 'rst')
    print("Converted README.md to rst")
except (IOError, ImportError):
    print("Could not convert README.md to rst. Falling back to Markdown", file=sys.stderr)
    LONG_DESCRIPTION = open('README.md').read()

REQUIREMENTS = [
    'argparse',
    'GitPython>=0.3.2.RC1',
    'Pillow>=2.3.0',
    'requests',
    ]

if sys.version_info <= (3,):
    REQUIREMENTS.append('configparser==3.5.0b2') # Using the beta for PyPy compatibility

setup(name='lolologist',
      version='0.5.1',
      description=('A utility that automatically generates an image macro from your webcam whenever '
                   'you commit to a git repository.'),
      long_description=LONG_DESCRIPTION,
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy',
          'Environment :: Console',
          'Operating System :: POSIX :: Linux',
          'Operating System :: MacOS :: MacOS X',
          'Topic :: Multimedia :: Graphics :: Capture',
          'Topic :: Utilities',
          'Topic :: Software Development :: Version Control',
      ],
      keywords=['git', 'camera', 'webcam', 'commit', 'macro', 'image', 'lol', 'lulz', 'version', 'control'],
      url='https://github.com/arusahni/lolologist',
      download_url='https://github.com/arusahni/lolologist/tarball/v0.5.1',
      author='Aru Sahni',
      author_email='arusahni@gmail.com',
      license='MPL 2.0',
      packages=['lolologist'],
      package_data={'lolologist':['LeagueGothic-Regular.otf', 'tranzlator.json']},
      include_package_data=True,
      install_requires=REQUIREMENTS,
      entry_points={
          'console_scripts': ['lolologist=lolologist.lolologist:main'],
      },
      zip_safe=False)
