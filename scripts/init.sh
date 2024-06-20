#!/bin/bash

set -e

poetry run poetry install

cp ./resources/tesseract/__init__.pyi ./.venv/Lib/site-packages/tesserocr/__init__.pyi

git submodule init
git submodule update