FROM python:3.11-slim
WORKDIR /app
COPY data-service /app/worker
RUN pip install --no-cache-dir -r /app/worker/requirements.txt
CMD ["python", "-u", "worker/worker.py"]
