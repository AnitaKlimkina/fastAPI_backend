FROM python:3-alpine

WORKDIR /app

ADD requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt

COPY api/ ./app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]