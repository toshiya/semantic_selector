# Model Training

Here, we describe how to generate models for input topic identification.

## Setup

### Mac OSX

Install following software to your local machine.

* Local MySQL server
* Python 3.5+
* Morphological Analyzer ([Mecab](https://github.com/taku910/mecab))

```bash
brew install mysql pyenv mecab mecab-ipadic

# install python3.5.1+
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

# Caution!!! This delete all exisiting data in inputs table !!!
mysql -uroot -p register_form < data/training_data_jp.sql
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

## Run the training script

After prepareing the training data in local MySQL server,
run the training script to generate models.

```bash
$ PYTHONPATH=projects  ./projects/bin/train_model.py --epochs 400                                                                       Using TensorFlow backend.
model type: nn_fc
Train on 2610 samples, validate on 652 samples
Epoch 1/400
2017-10-20 13:52:44.301857: W tensorflow/core/platform/cpu_feature_guard.cc:45] The TensorFlow library wasn't compiled to use SSE4.2 instructions, but these are available on your machine and could speed up CPU computations.
2017-10-20 13:52:44.301876: W tensorflow/core/platform/cpu_feature_guard.cc:45] The TensorFlow library wasn't compiled to use AVX instructions, but these are available on your machine and could speed up CPU computations.
2017-10-20 13:52:44.301880: W tensorflow/core/platform/cpu_feature_guard.cc:45] The TensorFlow library wasn't compiled to use AVX2 instructions, but these are available on your machine and could speed up CPU computations.
2017-10-20 13:52:44.301883: W tensorflow/core/platform/cpu_feature_guard.cc:45] The TensorFlow library wasn't compiled to use FMA instructions, but these are available on your machine and could speed up CPU computations.
2610/2610 [==============================] - 0s - loss: 3.8752 - acc: 0.0398 - val_loss: 3.7276 - val_acc: 0.1902
Epoch 2/400
2610/2610 [==============================] - 0s - loss: 3.7344 - acc: 0.1379 - val_loss: 3.5656 - val_acc: 0.3328
Epoch 3/400
2610/2610 [==============================] - 0s - loss: 3.5887 - acc: 0.2115 - val_loss: 3.4212 - val_acc: 0.3666

... (some output lines)

Test loss: 0.78047495605
Test accuracy 0.835889570918

# of test data: 652
# of training_data: 2610
```

If the script successfully finished,
you can find model (labels, and dictionary) files under `models` dirctory.

```bash
$ ls -lrt models
total 29848
-rw-r--r--  1 toshiya.komoda toshiya.komoda   15200796 10 20 13:14 nn_fc_model.h5
-rw-r--r--  1 toshiya.komoda toshiya.komoda        975 10 20 13:14 labels.pickle
-rw-r--r--  1 toshiya.komoda toshiya.komoda      73531 10 20 13:14 inputs.dict
```

 These files are used by [API Server](/docs/api_server.md).
