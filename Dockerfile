FROM python:3.8.0

RUN mkdir /code \
&&apt-get update \
&&apt-get -y install freetds-dev \
&&apt-get -y install unixodbc-dev
COPY locustfile.py /code
COPY settings.py /code
COPY run.sh /code
COPY requirements.txt /code
RUN pip install -r /code/requirements.txt -i https://pypi.douban.com/simple
WORKDIR /code

CMD ["/bin/bash","run.sh"]
