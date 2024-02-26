.. _usage_install:

.. include:: ../_include/head.rst

.. include:: ../_include/warn_develop.rst

================
2 - Installation
================

Ansible
*******

See `the documentation <https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#pip-install>`_ on how to install Ansible.

**Make sure to read** the `Ansible best-practices <https://docs.ansible.com/ansible/2.8/user_guide/playbooks_best_practices.html#directory-layout>`_ on how to use Ansible!

----

Demo
****

Check out the demo at: `demo.webui.ansibleguy.net <https://demo.webui.ansibleguy.net>`_

Login: User :code:`demo`, Password :code:`Ansible1337`

----

Install
*******

Requires Python >=3.10

.. code-block:: bash

    python3 -m pip install ansibleguy-webui

**Using docker**:

.. code-block:: bash

    docker image pull ansible0guy/webui:latest


Start
*****

**TLDR**:

.. code-block:: bash

    cd $PLAYBOOK_DIR
    python3 -m ansibleguy-webui



**Using docker**:

.. code-block:: bash

    docker run -d --name ansible-webui --publish 127.0.0.1:8000:8000 ansible0guy/webui:latest


**Details**:

See: :ref:`Usage - Run <usage_run>`


Now you can open the Ansible-WebUI in your browser: `http://localhost:8000 <http://localhost:8000>`_

----

Proxy
*****

You can find a nginx config example here: `Nginx config example <https://github.com/ansibleguy/webui/blob/latest/examples/nginx.conf>`_

----

Service
*******

You might want to create a service-user:

.. code-block:: bash

    sudo useradd ansible-webui --shell /usr/sbin/nologin --create-home --home-dir /home/ansible-webui


You can find a service config example here: `Systemd config example <https://github.com/ansibleguy/webui/blob/latest/examples/systemd_service.conf>`_

Enabling & starting the service:

.. code-block:: bash

    systemctl enable ansible-webui.service
    systemctl start ansible-webui.service

For production usage you should use a proxy like nginx in from of the Ansible-WebUI webservice!
