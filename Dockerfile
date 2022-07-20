FROM python:3.8-slim-buster

WORKDIR /usr/app/src

COPY . .
RUN pip3 install -r requirements.txt

CMD [ "python3", "main.py"]