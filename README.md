# !!! Redirect !!!

This project has been moved to [O-X-L/ansible-webui](https://github.com/O-X-L/ansible-webui)!

----

# Basic WebUI for using Ansible

----

[![Lint](https://github.com/ansibleguy/webui/actions/workflows/lint.yml/badge.svg?branch=latest)](https://github.com/ansibleguy/webui/actions/workflows/lint.yml)
[![Test](https://github.com/ansibleguy/webui/actions/workflows/test.yml/badge.svg?branch=latest)](https://github.com/ansibleguy/webui/actions/workflows/test.yml)

**DISCLAIMER**: This is an **unofficial community project**! Do not confuse it with the vanilla [Ansible](https://ansible.com/) product!

The goal is to allow users to quickly install & run a WebUI for using Ansible locally.

Keep it simple.

----

## Setup

### Local - PIP

Requires Python >=3.10

```bash
# install
python3 -m pip install ansibleguy-webui

# run
python3 -m ansibleguy-webui
```

### Docker

Images: [webui](https://hub.docker.com/r/ansible0guy/webui), [webui-unprivileged](https://hub.docker.com/r/ansible0guy/webui-unprivileged), [webui-aws](https://hub.docker.com/r/ansible0guy/webui-aws)

```bash
docker image pull ansible0guy/webui:latest
docker run -d --name ansible-webui --publish 127.0.0.1:8000:8000 ansible0guy/webui:latest

# or with persistent data (volumes: /data = storage for logs & DB, /play = ansible playbook base-directory)
docker run -d --name ansible-webui --publish 127.0.0.1:8000:8000 --volume $(pwd)/ansible/data:/data --volume $(pwd)/ansible/play:/play ansible0guy/webui:latest
```

----

## Demo

Check out the demo at: [demo.webui.ansibleguy.net](https://demo.webui.ansibleguy.net)

Login: User `demo`, Password `Ansible1337`

----

## Usage

[Documentation](http://webui.ansibleguy.net/)

[![Docs Uptime](https://status.oxl.at/api/v1/endpoints/4--ansibleguy_ansible-webui-documentation/uptimes/7d/badge.svg)](https://status.oxl.at/endpoints/4--ansibleguy_ansible-webui-documentation)

[Alternative Link](https://ansible-webui.readthedocs.io/)

----

## Contribute

Feel free to contribute to this project using [pull-requests](https://github.com/ansibleguy/webui/pulls), [issues](https://github.com/ansibleguy/webui/issues) and [discussions](https://github.com/ansibleguy/webui/discussions)!

Testers are also very welcome! Please [give feedback](https://github.com/ansibleguy/webui/discussions)

See also: [Contributing](https://github.com/ansibleguy/webui/blob/latest/CONTRIBUTE.md)

<img src="https://contrib.rocks/image?repo=ansibleguy/webui&max=5" />

----

## Roadmap

- [x] Ansible Config

  - [x] Static Playbook-Directory

  - [x] Git Repository support

- [ ] Users

  - [x] Management interface (Django built-in)

  - [x] Groups & Job Permissions

  - [ ] [LDAP integration](https://github.com/django-auth-ldap/django-auth-ldap)

  - [x] [SAML SSO integration](https://github.com/grafana/django-saml2-auth)

- [ ] Jobs

  - [x] Execute Ansible using [ansible-runner](https://ansible.readthedocs.io/projects/runner/en/latest/python_interface/)

    - [x] Scheduled execution (Cron-Format)

    - [x] Manual/immediate execution

    - [x] Custom Execution-Forms

    - [ ] Support for [ad-hoc commands](https://docs.ansible.com/ansible/latest/command_guide/intro_adhoc.html)

    - [ ] Support for [Process-Isolation](https://ansible.readthedocs.io/projects/runner/en/stable/standalone/#running-with-process-isolation)

  - [x] Job Logging

    - [x] Write job metadata to database

    - [x] Write full job-logs to Filesystem

  - [x] Secret handling (Connect, Become, Vault)

    - [x] User-specific job credentials

  - [x] Alerting on Failure

    - [x] E-Mail

    - [x] Support for external Plugins (*simple Interface for Scripts*)

- [ ] WebUI

  - [x] Job Dashboard

      Status, Execute, Time of last & next execution, Last run User, Links to Warnings/Errors

  - [x] Job Output

      Follow the jobs output in realtime

  - [ ] Job Errors

      UI that allows for easy error analysis. Access to logs and provide links to possible solutions

  - [x] Show Ansible Running-Config

  - [x] Show Ansible Collections

    - [ ] Check Collections for available updates (Galaxy + GitHub releases)

  - [x] Mobile Support

  - [ ] Multi-Language Support

- [ ] API

  - [x] Manage and execute Jobs

- [ ] Database

  - [ ] Support for MySQL

- [ ] Testing

  - [ ] Unit Tests

  - [ ] Integration Tests

    - [x] Basic WebUI checks

    - [x] API Endpoints

    - [ ] Permission system
