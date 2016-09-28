FROM python:3.5.2-alpine
MAINTAINER Matjaž Finžgar <matjaz@finzgar.net>

WORKDIR /app

RUN apk add --update \
	gcc \
	musl-dev

COPY . /app
RUN pip install -r /app/requirements.txt

EXPOSE 5000
CMD [ "python", "partis-rss.py" ]
