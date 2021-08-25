FROM python:3.9

COPY . /app

RUN pip install /app

CMD ["python", "-mantares_broker_bot"]
