FROM python:3.12-slim-trixie
LABEL authors="Chief-Zach"

COPY application .

RUN pip install -r requirements.txt

ENTRYPOINT ["uvicorn", "wsgi:app_factory", "--host", "0.0.0.0", "--port", "8000", "--factory", "--reload"]