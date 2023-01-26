#!/bin/bash
mkdir -p ./public
cp README.md dict2graph_docs/index.md
#cp logo.png dict2graph_docs/logo.png

mkdocs build --site-dir ./public --verbose
cp dict2graph_docs/DOCS_README.md ./public/README.md
