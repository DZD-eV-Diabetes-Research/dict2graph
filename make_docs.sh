#!/bin/bash

cp README.md docs/index.md
cp logo.png docs/logo.png

mkdocs build --site-dir ./public --verbose
cp docs/DOCS_README.md ./public/README.md
