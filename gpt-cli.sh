
pwd=$(pwd)

source ~/.venvs/chatgpt/bin/activate
mkdir -p ~/.gpt
cd ~/projects/gpt-cli
python3 chatgpt.py
deactivate

cd $pwd
