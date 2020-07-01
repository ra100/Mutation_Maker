FROM python:3.7.4-alpine
LABEL maintainer="Mutation Maker https://github.com/Merck/Mutation_Maker"

ENV CELERY_BROKER_URL redis://redis:6379/0
ENV CELERY_RESULT_BACKEND redis://redis:6379/0
ENV C_FORCE_ROOT true

RUN apk add --no-cache libev-dev==4.25-r0 build-base==0.5-r1

COPY requirements.txt /var/tmp/
RUN pip install six==1.11.0
RUN pip install -r /var/tmp/requirements.txt

ENV HOME=/mutation_maker

COPY . ${HOME}
EXPOSE 8000
WORKDIR ${HOME}

CMD gunicorn server:app --bind=0.0.0.0:8000