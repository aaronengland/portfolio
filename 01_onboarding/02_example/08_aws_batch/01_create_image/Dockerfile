
FROM python:3.9
    
# update package manager
RUN apt-get update

# update pip
RUN pip install --upgrade pip

# copy requirements
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# copy script into container
COPY script.py .

# run script when image is run
CMD ["python3", "script.py"]
