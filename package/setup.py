from setuptools import setup

APP = ['main.py']
DATAFILES = ['config.ini']
OPTIONS = {
    'argv_emulation': True
}

setup(
    app = APP,
    data_files = DATAFILES,
    options = {'py2app': OPTIONS},
    setup_requires = ['py2app'],
)
