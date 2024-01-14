# Ansible WebUI

This project was inspired by [ansible-semaphore](https://github.com/ansible-semaphore/semaphore).

The goal is to allow users to quickly install a WebUI for using Ansible locally.

Keep it simple.

**This project is still in active development! DO NOT USE IN PRODUCTION!**


----

## Contribute

Feel free to contribute to this project using [pull-requests](https://github.com/ansibleguy/ansible-webui/pulls), [issues](https://github.com/ansibleguy/ansible-webui/issues) and [discussions](https://github.com/ansibleguy/ansible-webui/discussions)!


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

  - [ ] Scheduled execution

  - [ ] Job Logging

    - [ ] Write job metadata to database

    - [ ] Write full job-logs to Filesystem

  - [ ] Secret handling (Connect, Become, Vault)


- [ ] WebUI

  - [ ] Show Ansible Running-Config

  - [ ] Show Ansible Collections

    - [ ] Check Collections for available updates (galaxy + github releases)
