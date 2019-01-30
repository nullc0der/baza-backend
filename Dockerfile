FROM alpine:latest
LABEL maintainer Prasanta Kakati <prasantakakati@ekata.social>
RUN apk update && apk add build-base linux-headers postgresql-client postgresql-dev libpq python3 python3-dev jpeg-dev zlib-dev libressl-dev libffi-dev curl
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python
ENV PATH="$HOME/.poetry/bin:${PATH}"
RUN poetry config settings.virtualenvs.create false
RUN mkdir /baza-back
WORKDIR /baza-back
COPY pyproject.toml poetry.lock /baza-back/
RUN poetry install --no-dev
COPY . /baza-back
CMD [ "sh", "start.sh" ]
