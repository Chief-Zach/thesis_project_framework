FROM python:3.12-slim
LABEL authors="Chief-Zach"

ENV DEBUG=1
COPY application .

RUN pip install -r app/requirements.txt

ENTRYPOINT ["/start_server.sh"]