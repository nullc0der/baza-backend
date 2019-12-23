FROM debian:buster
LABEL maintainer Prasanta Kakati <prasantakakati@ekata.social>
RUN apt-get update && \
    apt-get install --yes build-essential postgresql-client \
    libpq-dev libjpeg-dev zlib1g-dev libffi-dev curl \
    musl-dev libffi-dev libssl-dev python3 python3-dev
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN ln -s /usr/bin/pip3 /usr/bin/pip
RUN mkdir /baza-back
WORKDIR /baza-back
RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python
COPY pyproject.toml poetry.lock /baza-back/
RUN source $HOME/.poetry/env && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev
COPY . /baza-back
CMD [ "sh", "start.sh" ]
