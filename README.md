# Reference

- https://arxiv.org/abs/1608.06549

# Setup

Load answer data to local mysql server.

```
mysql -uxxx -p -e 'create database login_form'
mysql -uxxx -p -e login_form < data/inputs.sql
```

setup python3 and virtual env.

```
brew install pyenv
pyenv install 3.5.2
pip install virtualenv

# make virtual envrionment
virtualenv semantic
source semantic/bin/activate
cd projects
pip3 install -r requirements.txt
```

# Inference

```
cd projects
PYTHONPATH=.  ./bin/infer_test
```

# start API server

```
cd projects
PYTHONPATH=. FLASK_APP=./bin/api.py flask run
```
