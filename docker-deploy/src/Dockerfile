FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code

RUN apt-get update && apt-get install -y postgresql-client

ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/

RUN chmod +x run.sh
# RUN ./run.sh