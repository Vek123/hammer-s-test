FROM python:3.11-alpine

RUN apk update
RUN apk upgrade

WORKDIR /service/

COPY ./requirements/prod.txt ./

RUN pip3 install -r prod.txt

COPY ./services/phone_notification.py ./

CMD [ "python3", "phone_notification.py" ]
