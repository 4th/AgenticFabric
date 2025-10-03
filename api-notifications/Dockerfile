FROM python:3.11-slim
WORKDIR /app
COPY common /app/common
COPY api-notifications /app/svc
RUN pip install --no-cache-dir -r /app/common/requirements.txt -r /app/svc/requirements.txt
EXPOSE 8000
CMD ["uvicorn", "svc.app:app", "--host", "0.0.0.0", "--port", "8000"]
