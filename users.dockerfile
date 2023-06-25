FROM python:3

RUN mkdir -p /opt/src/users
WORKDIR /opt/src/users

COPY users/application.py ./application.py
COPY users/configuration.py ./configuration.py
COPY users/models.py ./models.py
COPY users/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/users"

ENTRYPOINT ["python", "./application.py"]