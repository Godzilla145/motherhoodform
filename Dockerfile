FROM python:3.11-slim

WORKDIR /app

COPY . /app/

ENV PYTHONUNBUFFERED=1
ENV PORT=8501
EXPOSE 8501

CMD ["python", "server.py"]
