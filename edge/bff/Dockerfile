FROM python:3.12-alpine

WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY bff/aea_bff ./aea_bff

USER nobody
CMD ["uvicorn", "aea_bff.runtime:app", "--host", "0.0.0.0", "--port", "8080", "--no-server-header"]
