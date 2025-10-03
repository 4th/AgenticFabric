FROM python:3.11-slim
WORKDIR /app
COPY common /app/common
COPY agent /app/agent
RUN pip install --no-cache-dir -r /app/common/requirements.txt -r /app/agent/requirements.txt
EXPOSE 8000
CMD ["uvicorn", "agent.app:app", "--host", "0.0.0.0", "--port", "8000"]
