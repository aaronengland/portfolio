
FROM python:3.9
    
WORKDIR usr/src/app

# copy requirements
COPY requirements.txt .

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# api.py
COPY api.py .

# functions.py
COPY functions.py .

# functions_counters.py
COPY functions_counters.py .

# functions_counters_pricing.py
COPY functions_counters_pricing.py .

# preprocessing.py
COPY preprocessing.py .

# cls_parser.pkl
COPY cls_parser.pkl .

# copy function code
COPY app.py .

# run script when image is run
CMD ["python", "-u", "app.py"]
