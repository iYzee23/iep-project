FROM python:3

RUN mkdir -p /opt/src/shop
WORKDIR /opt/src/shop

COPY shop/applicationOwner.py ./application.py
COPY shop/configuration.py ./configuration.py
COPY shop/models.py ./models.py
COPY ./requirements.txt ./requirements.txt
COPY ./decorator.py ./decorator.py

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/shop"

ENTRYPOINT ["python", "./application.py"]