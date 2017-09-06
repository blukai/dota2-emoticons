FROM mono:latest

RUN apt-get update \
  && apt-get install -y python3 python3-pip

WORKDIR /code
COPY . .

RUN pip3 install -r requirements.txt