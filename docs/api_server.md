# API Server

We provide a very simple API server implementation in order to
use the function from test codes written in other language than python
(e.g. Ruby with RSpec).

Currently, the API server does not have any authentication mechanism.

## Specification

We use swagger 2.0 to define the API spec
([swagger definition](/projects/docs/swagger.json)).

The auto-generated API docs is found in docs/api/.

- [overview](/docs/api/overview.md)
- [paths](/docs/api/paths.md)
- [definitions](/docs/api/definitions.md)
- [security](/docs/api/security.md)

# Launch API Server at local

Before launch API server, you have to [setup your python environment](/docs/training_model.md#setup
).


Execute below commands at the root directory.
The server will start at `localhost:5000`.

```bash
source venv/bin/activate
PYTHONPATH=projects FLASK_APP=./projects/bin/api.py flask run
```

# HTTP Request Example

curl

```
curl -X POST -H "Content-Type: application/json" http://localhost:5000/api/inference -d "{ \"html\" : \"<input type='text' name='mail_addr' placeholder='email address'>\"}"
```
