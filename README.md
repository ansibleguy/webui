# Ansible WebUI

[![Documentation](https://readthedocs.org/projects/ansible-webui/badge/?version=latest)](https://ansible-webui.readthedocs.io/en/latest/?badge=latest)
[![Lint](https://github.com/ansibleguy/ansible-webui/actions/workflows/lint.yml/badge.svg?branch=latest)](https://github.com/ansibleguy/ansible-webui/actions/workflows/lint.yml)
[![Test](https://github.com/ansibleguy/ansible-webui/actions/workflows/test.yml/badge.svg?branch=latest)](https://github.com/ansibleguy/ansible-webui/actions/workflows/test.yml)



The goal is to allow users to quickly install & run a WebUI for using Ansible locally.

Keep it simple.

**This project is still in early development! DO NOT USE IN PRODUCTION!**

----

## Setup

### Local - PIP

```bash
# install
python3 -m pip install ansible-webui

# run
python3 -m ansible-webui
```

### Docker

```bash
docker image pull ansible0guy/ansible-webui:<VERSION>
docker run -d --name ansible-webui --publish 127.0.0.1:8000:8000 --volume $(pwd)/ansible/data:/data --volume $(pwd)/ansible/play:/play ansible-webui:<VERSION>
```

----

## Demo

Check out the demo at: [demo.webui.ansibleguy.net](https://demo.webui.ansibleguy.net)

Login: User `demo`, Password `Ansible1337`

----

## Usage

[Documentation](http://ansible-webui.readthedocs.io/)

----

## Contribute

Feel free to contribute to this project using [pull-requests](https://github.com/ansibleguy/ansible-webui/pulls), [issues](https://github.com/ansibleguy/ansible-webui/issues) and [discussions](https://github.com/ansibleguy/ansible-webui/discussions)!

Testers are also very welcome! Please [give feedback](https://github.com/ansibleguy/ansible-webui/issues)

See also: [Contributing](https://github.com/ansibleguy/ansible-webui/blob/latest/CONTRIBUTE.md)

----

## Roadmap

- [x] Ansible Config

  - [x] Static Playbook-Directory

  - [ ] Git Repository support

- [ ] Users

  - [x] Management interface (Django built-in)

  - [x] Groups & Job Permissions

  - [ ] [LDAP integration](https://github.com/django-auth-ldap/django-auth-ldap)

  - [ ] [SAML SSO integration](https://github.com/grafana/django-saml2-auth)

- [ ] Jobs

  - [x] Execute Ansible using [ansible-runner](https://ansible.readthedocs.io/projects/runner/en/latest/python_interface/)

    - [x] Scheduled execution (Cron-Format)

    - [x] Manual/immediate execution

    - [ ] Support for [ad-hoc commands](https://docs.ansible.com/ansible/latest/command_guide/intro_adhoc.html)

  - [x] Job Logging

    - [x] Write job metadata to database

    - [x] Write full job-logs to Filesystem

  - [x] Secret handling (Connect, Become, Vault)

    - [x] User-specific job credentials

  - [ ] Alerting on Failure

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

- [ ] API

  - [x] Manage and execute Jobs

- [ ] Testing

  - [ ] Unit Tests

  - [ ] Integration Tests

    - [x] Basic WebUI checks

    - [x] API Endpoints

    - [ ] Permission system
