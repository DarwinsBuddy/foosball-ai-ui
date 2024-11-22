# if .venv does not exist, create it
if [ ! -d ".venv" ]; then
    ./setup.sh
fi
# activate the virtual environment
source .venv/bin/activate
# run the server
python -m web