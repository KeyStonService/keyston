FROM python:3.12-slim

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]

RUN apt-get update && apt-get install -y --no-install-recommends \
  ca-certificates \
  && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir python-docx==1.1.2 pyyaml==6.0.2

WORKDIR /work

COPY scripts/docx/convert.sh /usr/local/bin/convert.sh
RUN chmod +x /usr/local/bin/convert.sh

ENTRYPOINT ["/usr/local/bin/convert.sh"]
