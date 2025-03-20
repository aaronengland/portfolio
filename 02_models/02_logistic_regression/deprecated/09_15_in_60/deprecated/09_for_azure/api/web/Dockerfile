
FROM python:3.9
    
WORKDIR usr/src/app

# copy requirements
COPY requirements.txt .

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# api.py
COPY api.py .

# preprocessing.py
COPY preprocessing.py .

# cls_parser.pkl
COPY cls_parser.pkl .

# counters
COPY functions_counters.py .

# pricing
COPY functions_counters_pricing.py .

# copy function code
COPY app.py .

# run script when image is run
CMD ["python", "-u", "app.py"]
