FROM python:3.10.17-slim

ENV PYTHONUNBUFFERED=1


WORKDIR /rag-llm


COPY . /rag-llm

COPY requirements.txt /rag-llm/.
COPY .env /rag-llm/.env

RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]