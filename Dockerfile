FROM python:3.10-alpine

ARG AW_VERSION="0.0.5"

# BUILD CMD: docker build -t ansible-webui:0.0.4-dev --build-arg "AW_VERSION=0.0.4" .

# /ansible-webui can be used to mount an existing playbook-directory/-repo
RUN pip install --no-cache-dir --upgrade pip 2>/dev/null && \
    pip install --no-cache-dir ansible-webui==${AW_VERSION} && \
    mkdir -p /ansible-webui

WORKDIR /ansible-webui
EXPOSE 8000

CMD ["python3", "-m", "ansible-webui"]
