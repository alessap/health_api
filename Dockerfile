FROM python:3.7.7-alpine

WORKDIR /workdir

COPY main.py /workdir
COPY Pipfile.lock /workdir 
COPY Pipfile /workdir
COPY api/ /workdir/api

RUN pip3 install pipenv
RUN pipenv install --system

EXPOSE 8000
ENV FLASK_APP main.py

CMD ["flask", "run", "--host", "0.0.0.0", "--port", "8000"]
