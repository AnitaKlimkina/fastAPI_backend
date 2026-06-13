FROM python:3-alpine

ADD requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt

ADD database.py /app/
ADD models.py /app/

CMD python /app/models.py