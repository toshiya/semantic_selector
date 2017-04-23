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
pip3 install mysql-connector==2.1.4 gensim beautifulsoup4
```

# Inference

TODO
