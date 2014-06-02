from setuptools import setup

setup(name='lolologist',
      version='0.4.0',
      description='A utility that generates an image macro from your webcam whenever \
              you commit to a git repository.',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
          'Programming Language :: Python :: 2.6',
          'Environment :: Console',
          'Operating System :: POSIX :: Linux',
          'Operating System :: MacOS :: MacOS X',
          'Topic :: Multimedia :: Graphics :: Capture',
          'Topic :: Utilities',
          'Topic :: Software Development :: Version Control',
      ],
      url='https://github.com/arusahni/lolologist',
      author='Aru Sahni',
      author_email='arusahni@gmail.com',
      license='MPL 2.0',
      packages=['lolologist'],
      package_data={'lolologist':['LeagueGothic-Regular.otf', 'tranzlator.json']},
      include_package_data=True,
      install_requires=[
          'argparse',
          'GitPython>=0.3.2.RC1',
          'Pillow>=2.3.0',
          'requests',
          'configparser',
      ],
      entry_points = {
          'console_scripts': ['lolologist=lolologist.lolologist:main'],
      },
      zip_safe=False)
