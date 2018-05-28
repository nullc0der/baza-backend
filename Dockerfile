FROM alpine:latest
LABEL maintainer Prasanta Kakati <prasantakakati@ekata.social>
RUN apk update
RUN apk add build-base linux-headers postgresql-client postgresql-dev libpq python3 python3-dev
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN pip3 install pipenv
RUN mkdir /baza-back
WORKDIR /baza-back
COPY Pipfile /baza-back
COPY Pipfile.lock /baza-back
RUN pipenv install --system
COPY . /baza-back
CMD [ "sh", "start.sh" ]
