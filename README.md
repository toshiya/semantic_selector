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
python3.6 -m venv venv
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
bundle exec -- ruby manual_crawl.rb

$ driver.navigate.to "https://www.muji.net/store/cust/useradd/fullinfo?beforeUrl=terms"

# check the url has been already visited?
$ visited?(driver.current_url)

$ inputs = find_input_tags(driver)
$ fill_input_tags(inputs)
# check the filled numbers in your browser, and save the form with the label.
# then, labeled data will be in your local mysql.
$ save(driver, inputs[2], "pc_email")

$ radios = find_radio_box(driver)
$ radios[0].click()
$ save(driver, radios[0], "gender")

$ selects = find_select_box(driver)
$ selects[0].click()
$ save(driver, selects[0], "birhtday_year")

$ checks = find_check_box(driver)
$ checks[0].click()
$ save(driver, checks[0], "mail_delivery")

# if the element is hidden, use js to click.
$ click_by_js(driver, radios[0])
```
