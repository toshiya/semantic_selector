
Under construction.

# API server

```bash
cd projects
PYTHONPATH=. FLASK_APP=./bin/api.py flask run

# call it in another console
curl -X POST -H "Content-Type: application/json" http://localhost:5000/api/inference -d '{ "html" : "<input type='text' name='mail_addr' placeholder='メールアドレス'>"}'
```
