FROM python:3.10-alpine

ARG AW_VERSION="0.0.7"

# BUILD CMD: docker build -t ansible-webui:<VERSION> --build-arg "AW_VERSION=<VERSION>" .
# BUILD LATEST: docker build -t ansible-webui:latest --build-arg "AW_VERSION=latest" .

# /ansible-webui can be used to mount an existing playbook-directory/-repo
RUN apk add --no-cache git && \
    pip install --no-cache-dir --upgrade pip 2>/dev/null && \
    pip install --no-cache-dir "git+https://github.com/ansibleguy/ansible-webui.git@${AW_VERSION}" && \
    mkdir -p /ansible-webui

WORKDIR /ansible-webui
EXPOSE 8000

CMD ["python3", "-m", "ansible-webui"]
