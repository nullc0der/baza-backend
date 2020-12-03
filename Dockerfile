FROM python:3.6
LABEL maintainer Prasanta Kakati <prasantakakati@ekata.social>
# TODO: Needs to check dependency thoroughly
RUN apt-get update && \
    apt-get install --yes build-essential postgresql-client \
    libpq-dev libjpeg-dev zlib1g-dev libffi-dev curl \
    musl-dev libffi-dev libssl-dev poppler-utils libmagic1
RUN mkdir /baza-back
WORKDIR /baza-back
RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python
COPY pyproject.toml poetry.lock /baza-back/
RUN . $HOME/.poetry/env && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev
COPY . /baza-back
CMD [ "sh", "start.sh" ]
