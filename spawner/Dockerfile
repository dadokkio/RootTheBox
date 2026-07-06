FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY spawner.py .

EXPOSE 8080

CMD ["python", "spawner.py"]
