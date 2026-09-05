# Gate fixture for #332. Not a deployable image.
# Seeded PyYAML 5.3 must produce a fixable High/Critical finding.
FROM python:3.12-alpine@sha256:b64631e04e4920160c50fbe8d8df828f7f35f06f425cb44aa09bca53e708a35a
RUN pip install --no-cache-dir pyyaml==5.3
