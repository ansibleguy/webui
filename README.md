# Ansible WebUI

[![Documentation](https://readthedocs.org/projects/ansible-webui/badge/?version=latest)](https://ansible-webui.readthedocs.io/en/latest/?badge=latest)
[![Lint](https://github.com/ansibleguy/ansible-webui/actions/workflows/lint.yml/badge.svg?branch=latest)](https://github.com/ansibleguy/ansible-webui/actions/workflows/lint.yml)
[![Test](https://github.com/ansibleguy/ansible-webui/actions/workflows/test.yml/badge.svg?branch=latest)](https://github.com/ansibleguy/ansible-webui/actions/workflows/test.yml)



The goal is to allow users to quickly install & run a WebUI for using Ansible locally.

This is archived by [distributing it using pip](https://pypi.org/project/ansible-webui/).

Keep it simple.

**This project is still in early development! DO NOT USE IN PRODUCTION!**

----

## Setup

```
# install
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

Testers are also very welcome! Please [give feedback](https://github.com/ansibleguy/ansible-webui/issues)

See also: [Contributing](https://github.com/ansibleguy/ansible-webui/blob/latest/CONTRIBUTE.md)

----

## Comparison

There are multiple Ansible WebUI products - how do they compare to this product?

* **[Ansible AWX](https://www.ansible.com/community/awx-project) / [Ansible Automation Platform](https://www.redhat.com/en/technologies/management/ansible/pricing)**

   If you want an enterprise-grade solution - you might want to use these official products.

   They have many neat features and are designed to run in containerized & scalable environments.

   The actual enterprise solution named 'Ansible Automation Platform' can be pretty expensive.


* **[Ansible Semaphore](https://github.com/ansible-semaphore/semaphore)**

   Semaphore is a pretty lightweight WebUI for Ansible.

   It is a single binary and built from Golang (backend) and Node.js/Vue.js (frontend).

   Ansible job execution is done using [custom implementation](https://github.com/ansible-semaphore/semaphore/blob/develop/db_lib/AnsiblePlaybook.go).

   The project is [managed by a single maintainer and has some issues](https://github.com/ansible-semaphore/semaphore/discussions/1111). It seems to develop in the direction of large-scale containerized deployments.

   The 'Ansible-WebUI' project was inspired by Semaphore.


* **This project**

   It is built to be lightweight.

   As Ansible already requires Python3 - I chose it as primary language.

   The backend stack is built of [gunicorn](https://gunicorn.org/)/[Django](https://www.djangoproject.com/) and the frontend consists of Django templates and basic JS.

   Ansible job execution is done using the official [ansible-runner](https://ansible.readthedocs.io/projects/runner/en/latest/python_interface/) library!

   Target users are small to medium businesses and Ansible users which just want a UI to run their playbooks.

----

## Roadmap

- [x] Ansible Config

  - [x] Static Playbook-Directory

  - [ ] Git Repository support

- [ ] Users

  - [x] Management interface (Django built-in)

  - [ ] Groups & Job Permissions

  - [ ] [LDAP integration](https://github.com/django-auth-ldap/django-auth-ldap)

- [ ] Jobs

  - [x] Execute Ansible using [ansible-runner](https://ansible.readthedocs.io/projects/runner/en/latest/python_interface/)

    - [x] Scheduled execution (Cron-Format)

    - [x] Manual/immediate execution

    - [ ] Support for [ad-hoc commands](https://docs.ansible.com/ansible/latest/command_guide/intro_adhoc.html)

  - [ ] Job Logging

    - [x] Write job metadata to database

    - [ ] Write full job-logs to Filesystem

  - [x] Secret handling (Connect, Become, Vault)

    - [ ] User-specific credentials

- [ ] WebUI

  - [x] Job Dashboard

      Status, Execute, Time of last & next execution, Last run User, Links to Warnings/Errors

  - [ ] Job Output

      Follow the jobs output in realtime

  - [ ] Job Errors

      UI that allows for easy error analysis. Access to logs and provide links to possible solutions

  - [ ] Show Ansible Running-Config

  - [ ] Show Ansible Collections

    - [ ] Check Collections for available updates (galaxy + github releases)

- [ ] API

  - [x] Manage and execute Jobs
