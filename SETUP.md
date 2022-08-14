Install locally or on a VM:

```
pip3 install -U pip
#iconv -f us-ascii -t UTF-8 requirements.txt -o requirements.txt # If your requirements file is wrong encoding format
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
# gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 # Optionally host with guvicorn
```

Install using Docker: 

```
# Edit container if using NGINX or related backend: https://fastapi.tiangolo.com/deployment/docker/
docker build -t ispothate .
docker run -d --name containername -p 8000:8000 ispothate
```

