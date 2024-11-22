# Setup python
rm -fR .venv
python -m venv .venv
. .venv/bin/activate &&
pip install --upgrade pip &&
pip install setuptools &&
pip install -r requirements.txt