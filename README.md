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
$ PYTHONPATH=projects  ./projects/bin/infer_test
failing inferences
html, estimated, correct
<input style="float: right; margin-right: 115px; width: 320px;" placeholder="もう一度パスワードを入力" type="password" name="password_cfm" id="" ng-model="password_cfm" ng-required="true" match="password" class="ng-invalid ng-dirty ng-valid-parse ng-valid-required ng-invalid-mismatch ng-touched" required="required">,password,password_confirmation
<input type="checkbox" class="use-cookie-personalization-field hidden" name="user[use_cookie_personalization]" value="1" style="display: inline-block;">,service_term,user_customization

# of test data: 39
# of training_data: 757
# of vector elements: 500
Model Fitting Score, 0.948480845443
Accuracy, 0.9487179487179487
Recall, 0.9487179487179487
unkown ratio in test data, 0.0
```

# start API server at local

```bash
cd projects
PYTHONPATH=. FLASK_APP=./bin/api.py flask run

# call it in another console
curl -X POST -H "Content-Type: application/json" http://localhost/api/inference -d '{ "html" : "<input type='text' name='mail_addr' placeholder='メールアドレス'>"}'
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

# start api server, used by interactive shell to infere labels.
cd projects
PYTHONPATH=. FLASK_APP=./bin/api.py flask run

# open antther tab and start interactive shell
bundle exec -- ruby manual_crawl.rb

$ load_page "https://www.muji.net/store/cust/useradd/fullinfo?beforeUrl=terms"

# start interactive shell for labeling
$ collect
```


