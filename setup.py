from setuptools import setup

setup(name='lolologist',
      version='0.1',
      description='A utility that generates an image macro from your webcam whenever \
        you commit to a git repository.',
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: Python :: 2.6',
        'Topic :: Text Processing :: Linguistic',
        'Environment :: Console',
        'Operating System :: POSIX :: Linux',
        'Topic :: Multimedia :: Graphics :: Capture',
        'Topic :: Utilities',
        'Topic :: Software Development :: Version Control',
      ],
      url='https://github.com/arusahni/lolologist',
      author='Aru Sahni',
      author_email='arusahni@gmail.com',
      license='MPL 2.0',
      packages=['lolologist'],
      install_requires=[
        'argparse',
        'GitPython',
        'Pillow',
      ],
      entry_points = {
        'console_scripts': ['lolologist=lolologist.lolologist:main'],
      },
      zip_safe=False)
