# Ansible WebUI

[![Documentation](https://readthedocs.org/projects/ansible-webui/badge/?version=latest)](https://ansible-webui.readthedocs.io/en/latest/?badge=latest)
[![Lint](https://github.com/ansibleguy/ansible-webui/actions/workflows/lint.yml/badge.svg?branch=latest)](https://github.com/ansibleguy/ansible-webui/actions/workflows/lint.yml)
[![Test](https://github.com/ansibleguy/ansible-webui/actions/workflows/test.yml/badge.svg?branch=latest)](https://github.com/ansibleguy/ansible-webui/actions/workflows/test.yml)

This project was inspired by [ansible-semaphore](https://github.com/ansible-semaphore/semaphore).

The goal is to allow users to quickly install a WebUI for using Ansible locally.

This is achived by [distributing it using pip](https://pypi.org/project/ansible-webui/).

Keep it simple.

**This project is still in early development! DO NOT USE IN PRODUCTION!**

----

## Setup

```
# requirements
python3 -m pip install -r requirements.txt

# webui
python3 -m pip install ansible-webui

# run
python3 -m ansible-webui
```

----

## Usage

[Documentation](http://ansible-webui.readthedocs.io/)

----

## Contribute

Feel free to contribute to this project using [pull-requests](https://github.com/ansibleguy/ansible-webui/pulls), [issues](https://github.com/ansibleguy/ansible-webui/issues) and [discussions](https://github.com/ansibleguy/ansible-webui/discussions)!

See also: [Contributing](https://github.com/ansibleguy/ansible-webui/blob/latest/CONTRIBUTE.md)


----

## Roadmap

- [ ] Ansible Config

  - [ ] Static Playbook-Directory

  - [ ] Git Repository support

- [ ] Users

  - [ ] Management interface (Django built-in)

  - [ ] Groups & Permissions

  - [ ] [LDAP integration](https://github.com/django-auth-ldap/django-auth-ldap)

- [ ] Jobs

  - [ ] Execute Ansible using its [Python API](https://docs.ansible.com/ansible/latest/dev_guide/developing_api.html)

  - [ ] Ad-Hoc execution

  - [ ] Scheduled execution (Cron-Format)

  - [ ] Job Logging

    - [ ] Write job metadata to database

    - [ ] Write full job-logs to Filesystem

  - [ ] Secret handling (Connect, Become, Vault)


- [ ] WebUI

  - [ ] Show Ansible Running-Config

  - [ ] Show Ansible Collections

    - [ ] Check Collections for available updates (galaxy + github releases)
