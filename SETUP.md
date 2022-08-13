```
pip3 install -U pip
pip install -r requirements.txt
iconv -f us-ascii -t UTF-8 requirements.txt -o requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```
