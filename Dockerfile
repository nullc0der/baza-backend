FROM python:3.7
LABEL maintainer Prasanta Kakati <prasantakakati@ekata.social>
# TODO: Needs to check dependency thoroughly
RUN apt-get update && \
    apt-get install --yes build-essential postgresql-client \
    libpq-dev libjpeg-dev zlib1g-dev libffi-dev curl \
    musl-dev libffi-dev libssl-dev poppler-utils libmagic1 ca-certificates
RUN mkdir /baza-back
WORKDIR /baza-back
ENV POETRY_HOME=/opt/poetry
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN curl -sSL https://install.python-poetry.org | python3 -
COPY pyproject.toml poetry.lock /baza-back/
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev
COPY . /baza-back
CMD [ "sh", "start.sh" ]
