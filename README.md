# Reference

- https://arxiv.org/abs/1608.06549

# Setup

```bash
brew install mysql pyenv mecab mecab-ipadic

mysql -uxxx -p -e 'create database register_form'
mysql -uxxx -p register_form < data/register_form.sql

# python3.5+
pyenv install 3.5.2
pyenv local 3.5.2
python -m venv venv
source venv/bin/activate
pip3 install -r projects/requirements.txt

```

# Inference

```bash
$ PYTHONPATH=projects  ./projects/bin/infer_test --threashold 10 --ratio_test 0.05
failing inferences

estimated, correct
family_name,address_town
...
address_town,address_street

# of test data: 154
# of training_data: 3108
# of vector elements: 500
Model Fitting Score, 0.90444015444
Accuracy, 0.7987012987012987
Recall, 0.7987012987012987
unkown ratio in test data, 0.0
```

# start API server at local

```bash
cd projects
PYTHONPATH=. FLASK_APP=./bin/api.py flask run

# call it in another console
curl -X POST -H "Content-Type: application/json" http://localhost:5000/api/inference -d '{ "html" : "<input type='text' name='mail_addr' placeholder='メールアドレス'>"}'
```

# Collect new training data

Provide some utitlity functions to label input forms.
require Ruby2.4+

```bash
brew install chromedriver
cd tool
gem install bundler
bundle install --path vendor/bundle

mysql.server start

# start api server, used by interactive shell to infer labels.
cd projects
PYTHONPATH=. FLASK_APP=./bin/api.py flask run

# open another tab and start interactive shell
bundle exec -- ruby manual_crawl.rb

$ load_page "https://www.muji.net/store/cust/useradd/fullinfo?beforeUrl=terms"

# start labeling for the loaded page
$ collect
```


