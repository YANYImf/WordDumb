#!/usr/bin/env python3

import json
import platform
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

from calibre.utils.config import config_dir
from calibre_plugins.worddumb.config import prefs

NLTK_VERSION = '3.6.2'
NUMPY_VERSION = '1.20.3'
PLUGIN_PATH = Path(config_dir).joinpath('plugins/WordDumb.zip')


def load_json(filepath):
    with zipfile.ZipFile(PLUGIN_PATH) as zf:
        with zf.open(filepath) as f:
            return json.load(f)


def install_libs(abort=None, log=None, notifications=None):
    pip_install('nltk', NLTK_VERSION)
    download_nltk_data()
    if prefs['x-ray']:
        pip_install('numpy', NUMPY_VERSION,
                    f'{sys.version_info.major}{sys.version_info.minor}')


def download_nltk_data():
    import nltk

    nltk_data_path = Path(config_dir).joinpath('plugins/worddumb-nltk')
    nltk_data_path_str = str(nltk_data_path)
    download_nltk_model(nltk_data_path, 'corpora', 'wordnet')  # morphy
    if prefs['x-ray']:
        models = [
            ('tokenizers', 'punkt'),  # word_tokenize
            ('taggers', 'averaged_perceptron_tagger'),  # pos_tag
            ('chunkers', 'maxent_ne_chunker'),  # ne_chunk
            ('corpora', 'words')
        ]
        for parent, model in models:
            download_nltk_model(nltk_data_path, parent, model)

    if nltk_data_path_str not in nltk.data.path:
        nltk.data.path.append(nltk_data_path_str)


def download_nltk_model(data_folder, parent, model):
    import nltk

    path = data_folder.joinpath(f'{parent}/{model}')
    if not path.is_dir():
        nltk.download(model, str(data_folder))
        path.with_suffix('.zip').unlink()


def pip_install(package, version, py_version=None):
    folder = Path(config_dir).joinpath(
        f'plugins/worddumb-libs/{package}{version}')
    if py_version:
        folder = folder.joinpath(py_version)

    if not folder.is_dir():
        for d in folder.parent.glob(f'{package}*'):
            shutil.rmtree(d)  # delete old package

        pip = 'pip3'
        # stupid macOS loses PATH when calibre is not started from terminal
        if platform.system() == 'Darwin':
            pip = '/usr/local/bin/pip3'  # Homebrew
            if not Path(pip).is_file():
                pip = '/usr/bin/pip3'  # built-in
        if py_version:
            subprocess.check_call(
                [pip, 'install', '-t', folder, '--python-version',
                 py_version, '--no-deps', f'{package}=={version}'])
        else:
            subprocess.check_call(
                [pip, 'install', '-t', folder, f'{package}=={version}'])
            # calibre has regex and it has .so file like numpy
            if package == 'nltk':
                for f in folder.glob('regex*'):
                    shutil.rmtree(f)

    if (p := str(folder)) not in sys.path:
        sys.path.append(p)
