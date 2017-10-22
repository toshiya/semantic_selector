[![CircleCI](https://circleci.com/gh/toshiya/semantic_selector.svg?style=svg)](https://circleci.com/gh/toshiya/semantic_selector)

**This project is now in experimental stage.**

# What's the purpose of this project?

In general, we would like to investigate the following question.

「Can machine learning make UI testing easier?」

Although there has been bunch of efforts to make UI testing easier, it is still not easy for normal developers.

Here, we would like to solve a "input topic identitication" problem in UI testing, as a first step to answer the above question.

# Input Topic Identification With Machine Learning

[![figure of input topic idenfitication](
https://gist.githubusercontent.com/toshiya/722357d3c8d1c22511594640d21db749/raw/702a890f16b6d663b63062911e1a9f1bc47c5230/Introduce_Machine_Learning_into_UI_Tests.png)](https://www.slideshare.net/ToshiyaKomoda/introduce-machine-learning-into-ui-tests)

Previously, this problem has been formalized as a machine learning problem in the following research paper by Jun-Wei Lin.

[Using Semantic Similarity for Input Topic Identification in Crawling-based Web Application Testing](https://arxiv.org/abs/1608.06549)

Suppose, we would like to make UI tests for user login page. Possible test implmentation with Capybara may looks like,

```
visit "https://test-target.com/login"

# find an input field whose name is "emailAddress", and fill in the value
fill_in "emailAddress",  with: "foo@var.com"

# find an input field whose name is "passwd", and fill in the value
fill_in "passwd", with: "password"

# find an button whose name is "btnNext", and click it
find('#btnNext').click
```

The problem of this implementation is that we have to know id or name attributes of text fileds. In this fashion, we have to understand the DOM structure of the test target page and have to manage id or name values as test assets. Considering the UI components are very likely to change, this test assets management tend to be tedious in making and maintaining your UI test suites.

We would like to make the test implementation like this.

```
visit "https://test-target.com/login"

# without any hard coded DOM related value, this function can find approriate input fields,
# fill in approriate values, and click next button
login_with_machine_learning
```

No need to understand the structure of test target pages. All the details would be properly handled by machine learning models.

That would simplify UI test implementation a lot in general.

# Documentation

Currently, this repo includes,

1. scripts to collect training data ([detail](/docs/collecting_training_set.md))
2. scripts to train models ([detail](/docs/training_model.md))
3. API Server to provide inference API([detail](/docs/api_server.md))

At the time, we do not provide any integration in popular test framework
you have to implement additional logic to integrate
the input topic identitication API in your test scripts.

We have a plan to integrate the input
topic identitication API to some
test framework in future.

# Contact

Feel free to contact me about this project.

- E-Mail: toshiya.komoda_at_gmail.com
- Twitter: [@toshiya_komoda](https://twitter.com/toshiya_komoda)
