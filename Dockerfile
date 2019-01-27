FROM alpine:latest
LABEL maintainer Prasanta Kakati <prasantakakati@ekata.social>
RUN apk update && apk add build-base linux-headers postgresql-client postgresql-dev libpq python3 python3-dev jpeg-dev zlib-dev libressl-dev libffi-dev
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN pip3 install pipenv
RUN mkdir /baza-back
WORKDIR /baza-back
COPY requirements.txt /baza-back
RUN pip install -r requirements.txt
COPY . /baza-back
CMD [ "sh", "start.sh" ]
