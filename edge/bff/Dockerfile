FROM python:3.12-alpine@sha256:b64631e04e4920160c50fbe8d8df828f7f35f06f425cb44aa09bca53e708a35a

WORKDIR /app
COPY requirements.txt requirements.lock ./
RUN pip install --no-cache-dir -r requirements.txt -c requirements.lock
COPY bff/aea_bff ./aea_bff

USER nobody
CMD ["uvicorn", "aea_bff.runtime:app", "--host", "0.0.0.0", "--port", "8080", "--no-server-header"]
