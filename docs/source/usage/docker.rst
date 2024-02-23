.. _usage_docker:

.. include:: ../_include/head.rst

.. include:: ../_include/warn_develop.rst

======
Docker
======

You can find the dockerfiles and scripts used to build the images `in the Repository <https://github.com/ansibleguy/ansible-webui/tree/latest/docker>`_

Ansible Requirements
********************

Our `docker image ansible0guy/ansible-webui <https://hub.docker.com/repository/docker/ansible0guy/ansible-webui>`_ enables you to install Ansible dependencies on container startup.

Files inside the container:

* Python3 Modules: :code:`/play/requirements.txt`
* `Ansible Roles & Collections <https://docs.ansible.com/ansible/latest/collections_guide/collections_installing.html#install-multiple-collections-with-a-requirements-file>`_: :code:`/play/requirements.yml`

    * Only Ansible Roles: :code:`/play/requirements_roles.yml` or :code:`/play/roles/requirements.yml`
    * Only Ansible Collections: :code:`/play/requirements_collections.yml` or :code:`/play/collections/requirements.yml`

----

Unprivileged
************

There are images for running Ansible-WebUI as unprivileged user :code:`aw` with UID/GID :code:`8785` inside the container:

* Latest: :code:`ansible0guy/ansible-webui-unprivileged:latest`

* Unstable: :code:`ansible0guy/ansible-webui-unprivileged:unstable`

----

Persistent Data
***************

It might make sense for you to mount these paths in the container:

* :code:`/data` (:code:`AW_DB` & :code:`AW_PATH_LOG` env-vars) - for database & execution-logs
* :code:`/play` (:code:`AW_PATH_PLAY` env-var) - for static Ansible playbook base-directory

If you are running an :code:`unprivileged` image - you will have to allow the service-user to write to the directories. The UID needs to match!

Basic example:

.. code-block:: bash

    # add matching service-user on the root system
    sudo useradd ansible-webui --shell /usr/sbin/nologin --uid 8785 --user-group
    chown ansible-webui:ansible-webui ${YOUR_DATA_DIR}

----

AWS CLI Support
***************

There is also an image that has AWS-CLI support pre-enabled: :code:`ansible0guy/ansible-webui-aws:latest`

Its base-image is :code:`ansible0guy/ansible-webui-unprivileged:latest`

----

Custom build
************

If you want to build a custom docker image - make sure to set those environmental variables:

:code:`AW_VERSION=X.X.X AW_DOCKER=1 PYTHONUNBUFFERED=1`
