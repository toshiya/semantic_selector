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
