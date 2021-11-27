FROM python:3.9

WORKDIR /usr/app

COPY . .

RUN apt-get update -y

RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt

CMD uvicorn server:app --host 0.0.0.0 --port $PORT