FROM python:3.9.6

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get -y install gcc libpq-dev python3-dev netcat

COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src .

ENTRYPOINT ["./entrypoint.sh"]
CMD [ "python", "./main.py" ]
