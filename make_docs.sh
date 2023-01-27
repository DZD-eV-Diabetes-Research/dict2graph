#!/bin/bash
mkdir -p ./public
cp README.md dict2graph_docs/index.md

# adapt relativ image pathes and links to new path.
sed -i "s/dict2graph_docs\///g" dict2graph_docs/index.md
#sed -i "s/https:\/\/dzd-ev.github.io\/dict2graph-docs\///2g" dict2graph_docs/index.md

cp logo.png dict2graph_docs/logo.png

mkdocs build --site-dir ./public --verbose
cp dict2graph_docs/DOCS_README.md ./public/README.md
