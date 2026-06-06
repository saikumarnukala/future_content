FROM python:3.11-slim
RUN apt-get update && apt-get install -y ffmpeg fonts-montserrat && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
WORKDIR /app
CMD ["python", "pipeline/main.py"]
