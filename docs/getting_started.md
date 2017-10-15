# Getting Started

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

# Inference Accuracy Test

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
