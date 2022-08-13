# Start with a Python 3.8 base image
FROM python:3.8
# Make a work directory (/code) for the Docker image
WORKDIR /code
# Copy the requirements.txt file from the root directory to the working directory
COPY ./requirements.txt /code/requirements.txt
# Install all dependencies from root, forcing if needed
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
# Copy the contents of the root folder to the code folder
COPY . /code
# Run the app at 0.0.0.0 (localhost) at port 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# This will automatically sync with Azure's public IP if run from a VM
