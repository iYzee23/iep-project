FROM python:3

RUN mkdir -p /opt/src/shop
WORKDIR /opt/src/shop

COPY shop/applicationCourier.py ./application.py
COPY shop/configuration.py ./configuration.py
COPY shop/models.py ./models.py
COPY shop/requirements.txt ./requirements.txt
COPY shop/OrderContract.abi ./OrderContract.abi
COPY shop/OrderContract.bin ./OrderContract.bin
COPY ./decorator.py ./decorator.py

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/shop"

ENTRYPOINT ["python", "./application.py"]