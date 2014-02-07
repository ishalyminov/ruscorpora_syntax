#!/usr/bin/env sh

wget -O MaltEval.zip "https://drive.google.com/uc?id=0B1KaZVnBJE8_QnhqNE52T2FZWVE&export=download"
unzip MaltEval.zip
mv dist-20120206 malt_eval
rm -f MaltEval.zip
