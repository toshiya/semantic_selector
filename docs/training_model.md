# Train Models

Here, we describe how to generate models for input topic identification.

## Setup

### Mac OSX

Install following software to your local machine.

* Local MySQL server
* Python 3.5+
* Morphological Analyzer ([Mecab](https://github.com/taku910/mecab))

```bash
brew install mysql pyenv mecab mecab-ipadic

# install python3.5+
pyenv install 3.5.2
pyenv local 3.5.2

# we recommend you to use venv
python -m venv venv
source venv/bin/activate

# install required python packages, such as gensim, tensorflow, and keras.
pip3 install -r projects/requirements.txt
```

## Prepare Training Data

The training script assumes that all the training data is store in local MySQL server.
Before you train your model, you have to load training data to your local MySQL server.

You can use pre-included data,
or training data that you collect with [collecting scripts](/docs/collecting_training_set.md).

If you use pre-included data, execute commonds below.

```bash
# start MySQL server
mysql.server start

# create and load prepared training set.
mysql -uroot -p -e 'create database register_form'
mysql -uroot -p register_form < data/register_form.sql
```

### Training Data Format

The training data must be loaded into `inputs` table in `register_form` database.
Each record in the `inputs` table is 1 training sample with following columns.

|Column| Meaning |
|---|---|
|title| Title of the page where the input fields exists|
|url| URL of the page|
|html| HTML snippet of the input fields|
|parent_html| The parent HTML snippet of the input fields|
|label_html| The label HTML snippet of the input fields, if it exists in the page|
|topic| The topic of the input fields (manually verified)|

# Run the training script

After prepareing the training data in local MySQL server,
run the training script to generate models.

```bash
$ PYTHONPATH=projects  ./projects/bin/train_model.py

... (some output lines)

# of test data: 163
# of training_data: 3099
Accuracy, 0.8282208588957055
Recall, 0.8282208588957055
```

If the script successfully finished,
you can find model (labels, and dictionary) files under `models` dirctory.

```bash
(venv) [toshiya.komoda@o-09033-mac.local:git/github.com/semantic_selector]# ls -lrt models
total 29848
-rw-r--r--  1 toshiya.komoda  DENA\Domain Users  15200796 10 20 13:14 nn_fc_model.h5
-rw-r--r--  1 toshiya.komoda  DENA\Domain Users       975 10 20 13:14 labels.pickle
-rw-r--r--  1 toshiya.komoda  DENA\Domain Users     73531 10 20 13:14 inputs.dict
```

 These model files are used by [API Server](docs/api_server.md).
