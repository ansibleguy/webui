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

    * Only Ansible Roles: :code:`/play/requirements_roles.yml`
    * Only Ansible Collections: :code:`/play/requirements_collections.yml`

----

Persistent Data
***************

It might make sense for you to mount these paths in the container:

* :code:`/data` (:code:`AW_DB` & :code:`AW_PATH_LOG` env-vars) - for database & execution-logs
* :code:`/play` (:code:`AW_PATH_PLAY` env-var) - for static Ansible playbook base-directory

----

Custom build
************

If you want to build a custom docker image - make sure to set those environmental variables:

:code:`AW_VERSION=X.X.X AW_DOCKER=1 PYTHONUNBUFFERED=1`
