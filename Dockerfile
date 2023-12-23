FROM python:3.9-bookworm

WORKDIR /code

RUN pip install cairocffi numpy
