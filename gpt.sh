
pwd=$(pwd)

source ~/.venvs/chatgpt/bin/activate
mkdir -p ~/.gpt
cd ~/projects/chatgpt
python3 chatgpt.py
deactivate

cd $pwd
