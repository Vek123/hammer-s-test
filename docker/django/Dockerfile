FROM python:3.11-alpine

RUN apk update
RUN apk upgrade
RUN apk add gettext

WORKDIR /app/

RUN python3 -m venv .venv
RUN source .venv/bin/activate

COPY ./requirements/prod.txt ./

RUN pip3 install -r prod.txt

COPY ./referal/ ./referal/

ENV DJANGO_DEBUG=False
RUN python3 referal/manage.py compilemessages

WORKDIR /app/referal/

CMD [ "sh", "-c", "python3 manage.py migrate && gunicorn -b 0.0.0.0:8000 referal.wsgi:application" ]
