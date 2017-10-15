# Train models

You can train models with the prepared training data, or training data that you collect with [collecting scripts](/docs/collecting_training_set.md).

The training script assumes that all the training data is store in local MySQL server, database name is register_form and table name is inputs.

The training set database schema is like this.

|Column| Meaning |
|---|---|
|title| Title of the page where the input fields exists|
|url| URL of the page|
|html| HTML snippet of the input fields|
|parent_html| The parent HTML snippet of the input fields|
|label_html| The label HTML snippet of the input fields, if it exists in the page|
|label| The topic of the input fields (manually verified)|

# Setup training scripts

## Mac

```bash
brew install mysql pyenv mecab mecab-ipadic

# create and load prepared training set.
mysql -uroot -p -e 'create database register_form'
mysql -uroot -p register_form < data/register_form.sql

# install python3.5+
pyenv install 3.5.2
pyenv local 3.5.2

# we recommend you to use venv
python -m venv venv
source venv/bin/activate

# install required python packages, such as gensim, tensorflow, and keras.
pip3 install -r projects/requirements.txt
```

# Run training

After setting up your python environment and load the training set into the local MySQL server, you can run the training scripts to generate models.

```bash
$ PYTHONPATH=projects  ./projects/bin/infer_test

... (some output lines)

# of test data: 163
# of training_data: 3099
Accuracy, 0.8282208588957055
Recall, 0.8282208588957055
unkown ratio in test data, 0.0
```
