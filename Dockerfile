FROM python:3.6
LABEL maintainer Prasanta Kakati <prasantakakati@ekata.social>
RUN apt update && \
    apt install build-essential postgresql-client \
    libpq libpq-dev libjpeg-dev zlib1g-dev libffi-dev curl \
    musl-dev libffi-dev libssl-dev
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
