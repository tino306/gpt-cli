#!/bin/zsh

usr_dir=$(pwd)
source ~/.venvs/gpt-cli/bin/activate
mkdir -p ~/.gpt
cd ~/projects/gpt-cli
python3 gpt-cli.py
deactivate

cd $usr_dir
