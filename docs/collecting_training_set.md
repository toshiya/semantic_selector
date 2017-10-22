
To make the topic identitication as accurate as possible,
we have to collect HTML of text forms and give
topic labels for them.

We pre-include training data which contains
Japenese User Registration Page Information.
If you want to use pre-include data,
skip this step and go to
[Train Models](
/docs/training_model.md
).

# Collecting Training Data

Usually, it is time consuming tasks to make training
data for machine learning. To ease the process,
we provide a helper script.

The helper script can

* list all the input fields in the page
* infer topic candidates for the input fields
* store the topic and the input field data into local MySQL in approriate format.

# Set Up Helper Script

## Mac OS

First, install Chrome Web Broswer.

Then, install required packages via homebrew.

```bash
brew install chromedriver
brew install readline
```

Helper scripts are written in Ruby (2.3+ required).
Install gems.
```bash
cd tool
gem install bundler
bundle install --path vendor/bundle
```

Start and setup local MySQL Server.

```bash
mysql.server start

# create database and table
mysql -uroot -p -e 'create database register_form'
mysql -uroot -p register_form < data/register_form.sql

# check created table for training data
mysql -uroot -p register_form -e 'show create table inputs'

```

Start [the input topic identification API server](
/docs/api_server.md) in this repo.

```bash
source venv/bin/activate
PYTHONPATH=projects FLASK_APP=./projects/bin/api.py flask run
```

# Make training data using the helper script

Start the helper script.

```bash
cd tool/
# interactive prompt will launch
bundle exec -- ruby manual_crawl.rb

# make training data with web pages on the internet.
$ load_page "https://www.uniqlo.com/us/en/register/"
$ collect
...
```

Following commands are available in interactive shell.

|Command |  |
|---|---|
| load_page ${URL} | load the given url |
| load_highliter | load highliter to the page |
| collect | find input fields and make topic labels. |

In `collect` mode, follow instructions to label
topics for each input field.
During `collect` mode, corresponding input fields
should be highlighted with red box in the window
launched by selenium-webdriver.

The [video](https://youtu.be/AIPltHtIXAA) shows how it works.

After collecting training data, you can check the data in
MySQL.


```bash
mysql -uroot -p register_form -e 'select substring(html, 1, 100),topic from inputs'
Enter password:
+------------------------------------------------------------------------------------------------------+-----------------------+
| substring(html, 1, 100)                                                                              | topic                 |
+------------------------------------------------------------------------------------------------------+-----------------------+
| <input type="text" id="q" name="q" value="" placeholder="Search" autocomplete="off" aria-invalid="fa | search_window         |
| <input class="input-text email emailaddress required" type="text" id="dwfrm_profile_customer_email"  | pc_email              |
| <input class="input-text email emailaddress confirmemail required" type="text" id="dwfrm_profile_cus | pc_email_confirmation |
| <input class="input-text firstname validaddress required" type="text" id="dwfrm_profile_customer_fir | first_name            |
| <input class="input-text lastname validaddress required" type="text" id="dwfrm_profile_customer_last | family_name           |
| <input class="input-text password required" type="password" id="dwfrm_profile_login_password_d0huefj | password              |
| <input class="input-text passwordconfirm required" type="password" id="dwfrm_profile_login_passwordc | password_confirmation |
| <input type="text" id="q" name="q" value="" placeholder="Search" autocomplete="off" aria-invalid="fa | search_window         |
| <input class="input-text email emailaddress required" type="text" id="dwfrm_profile_customer_email"  | pc_email              |
| <input class="input-text email emailaddress confirmemail required" type="text" id="dwfrm_profile_cus | pc_email_confirmation |
| <input class="input-text firstname validaddress required" type="text" id="dwfrm_profile_customer_fir | first_name            |
| <input class="input-text lastname validaddress required" type="text" id="dwfrm_profile_customer_last | family_name           |
| <input class="input-text password required" type="password" id="dwfrm_profile_login_password_d0ubovi | password              |
| <input class="input-text passwordconfirm required" type="password" id="dwfrm_profile_login_passwordc | password_confirmation |
+------------------------------------------------------------------------------------------------------+-----------------------+
```

These records can be used in
[Train Models](
/docs/training_model.md
) Step.
