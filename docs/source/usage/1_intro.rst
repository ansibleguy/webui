.. _usage_intro:

.. include:: ../_include/head.rst

.. include:: ../_include/warn_develop.rst

=========
1 - Intro
=========

Comparison
**********

There are multiple Ansible WebUI products - how do they compare to this product?

* `Ansible AWX <https://www.ansible.com/community/awx-project>`_ / `Ansible Automation Platform <https://www.redhat.com/en/technologies/management/ansible/pricing>`_

   If you want an enterprise-grade solution - you might want to use these official products.

   They have many neat features and are designed to run in containerized & scalable environments.

   The actual enterprise solution named 'Ansible Automation Platform' can be pretty expensive.


* `Ansible Semaphore <https://github.com/ansible-semaphore/semaphore>`_

   Semaphore is a pretty lightweight WebUI for Ansible.

   It is a single binary and built from Golang (backend) and Node.js/Vue.js (frontend).

   Ansible job execution is done using `custom implementation <https://github.com/ansible-semaphore/semaphore/blob/develop/db_lib/AnsiblePlaybook.go>`_.

   The project is `managed by a single maintainer and has some issues <https://github.com/ansible-semaphore/semaphore/discussions/1111>`_. It seems to develop in the direction of large-scale containerized deployments.

   The 'Ansible-WebUI' project was inspired by Semaphore.


* **This project**

   It is built to be lightweight.

   As Ansible already requires Python3 - I chose it as primary language.

   The backend stack is built of `gunicorn <https://gunicorn.org/)/[Django](https://www.djangoproject.com/>`_ and the frontend consists of Django templates and basic/vanilla JS.

   Ansible job execution is done using the official `ansible-runner <https://ansible.readthedocs.io/projects/runner/en/latest/python_interface/>`_ library!

   Target users are small to medium businesses and Ansible users which just want a UI to run their playbooks.
