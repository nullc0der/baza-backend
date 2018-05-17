FROM alpine:latest
LABEL maintainer Prasanta Kakati <prasantakakati@ekata.social>
RUN apk update
RUN apk add libpq python python-dev py-pip
RUN mkdir /baza-back
WORKDIR /baza-back
COPY Pipfile /baza-back
COPY Pipfile.lock /baza-back
RUN pipenv install --system
COPY . /baza-back
CMD [ "sh", "start.sh" ]
