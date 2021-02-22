#!/usr/bin/env python3

import shutil
import sys
import zipfile
from pathlib import Path

from calibre.utils.config import config_dir
from calibre_plugins.worddumb.config import prefs

DB_VERSION = '1.2'
NUMPY_VERSION = '1.20.1'
PLUGIN_PATH = Path(config_dir).joinpath('plugins/WordDumb.zip')


def check_folder(folder_name, version, file_name, extract):
    extract_path = Path(config_dir).joinpath('plugins/'
                                             + folder_name + version)
    if not extract_path.is_dir():
        for f in Path(config_dir).joinpath('plugins').iterdir():
            if folder_name in f.name and f.is_dir():
                shutil.rmtree(f)  # delete old folder

        if extract:
            unzip(file_name, extract_path, PLUGIN_PATH)

    return extract_path


def unzip(file_name, extract_path, zip_file_path):
    with zipfile.ZipFile(zip_file_path, 'r') as zf:
        for f in zf.namelist():
            if not file_name or file_name in f:
                zf.extract(f, extract_path)


def install_libs():
    for d in zipfile.Path(PLUGIN_PATH).joinpath('.venv/lib').iterdir():
        sys.path.append(str(d.joinpath('site-packages')))

    download_nltk_data()
    if prefs['x-ray']:
        download_numpy()


def download_nltk_data():
    nltk_path = check_folder('worddumb-nltk', '', None, False)

    import nltk
    if not nltk_path.is_dir():
        nltk_path = str(nltk_path)
        nltk.download('wordnet', nltk_path)  # morphy
        nltk.download('punkt', nltk_path)  # word_tokenize
        nltk.download('averaged_perceptron_tagger', nltk_path)  # pos_tag
        # ne_chunk
        nltk.download('maxent_ne_chunker', nltk_path)
        nltk.download('words', nltk_path)
    nltk.data.path.append(nltk_path)


def unzip_db():
    db_path = check_folder('worddumb-db', DB_VERSION, 'dump.rdb', True)
    return str(db_path.joinpath('data'))


def download_numpy():
    numpy_path = check_folder('worddumb-numpy', NUMPY_VERSION, None, False)
    if not numpy_path.joinpath('numpy').is_dir():
        import platform
        import subprocess
        py_version = '{}{}'.format(
            sys.version_info.major, sys.version_info.minor)
        pip = 'pip3'
        if platform.system() == 'Darwin':
            pip = '/usr/local/bin/pip3'
        subprocess.check_call(
            [pip, 'install', '-U', 'pip', 'setuptools', 'wheel'])
        subprocess.check_call(
            [pip, 'download', '-d', numpy_path, '--python-version',
             py_version, '--no-deps', 'numpy==' + NUMPY_VERSION])
        for wheel in numpy_path.iterdir():
            unzip(None, numpy_path, wheel)
            wheel.unlink()
    sys.path.append(str(numpy_path))
