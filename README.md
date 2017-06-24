# Reference

- https://arxiv.org/abs/1608.06549

# Setup

Load answer data to local mysql server.

```
mysql -uxxx -p -e 'create database register_form'
mysql -uxxx -p register_form < data/register_form.sql
```

install mecab for japanese handling.
```
brew install mecab
brew install mecab-ipadic
```

setup python3 and virtual env.

```
brew install pyenv
# need python3.5+
pyenv install 3.5.2
pip install virtualenv

# make virtual envrionment
virtualenv venv
source venv/bin/activate
pip3 install -r projects/requirements.txt
```

# Inference

```
cd projects
PYTHONPATH=.  ./bin/infer_test
```

# start API server at local

```
cd projects
PYTHONPATH=. FLASK_APP=./bin/api.py flask run

# call it in another console
curl -X POST -H "Content-Type: application/json" http://localhost/api/inference -d '{ "html" : "<input type='text' name='mail_addr' placeholder='メールアドレス'>"}'
```
