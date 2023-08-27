from setuptools import setup

APP = ['main.py']
DATAFILES = ['config.ini', 'ffmpeg']
OPTIONS = {
    'argv_emulation': True,
    'arch': 'universal2',
    'iconfile': './icons/whisper.icns'
}

setup(
    app = APP,
    name = 'pySTT_Whisper_API',
    data_files = DATAFILES,
    options = {'py2app': OPTIONS},
    setup_requires = ['py2app']
)
