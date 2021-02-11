FROM ubuntu

RUN apt-get update
RUN apt-get --assume-yes  install python3
RUN apt-get --assume-yes  install python3-pip

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY settings.py ./
COPY orm.py ./
COPY kraken_manager.py ./
COPY telegram_manager.py ./
COPY kraken_bot.py ./
COPY telegram_bot.py ./
COPY main.py ./

CMD [ "python3", "./main.py" ]