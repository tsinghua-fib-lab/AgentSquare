
if [ $INSTALL_WEBARENA = false ]; then
## Tool/game24/babyi/pddl
pip3 install -r requirements.txt

## jericho
#apt update
#apt install -y build-essential libffi-dev curl
#export CC=/usr/bin/gcc
#export CXX=/usr/bin/g++

pip3 install https://github.com/MarcCote/downward/archive/faster_replan.zip
pip3 install https://github.com/MarcCote/TextWorld/archive/handcoded_expert_integration.zip
python3 -m spacy download en_core_web_lg
python3 -m spacy download en_core_web_sm
##

else
## Webarena
  playwright install
  Xvfb :99 -screen 0 1280x720x24 &
  export DISPLAY=:99
fi
