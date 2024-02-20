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

.. code-block:: bash

    python3 -m pip install ansible-webui

**Using docker**:

.. code-block:: bash

    docker image pull ansible0guy/ansible-webui:latest


Start
*****

**TLDR**:

.. code-block:: bash

    cd $PLAYBOOK_DIR
    python3 -m ansible-webui

**Details**:

.. code-block:: bash

    # change into your ansible-directory
    cd $PLAYBOOK_DIR

    # foreground
    python3 -m ansible-webui

    # background
    python3 -m ansible-webui > /tmp/aw.log 2> /tmp/aw.err.log &

    # at the first startup you will see the auto-generated credentials:

    [2024-01-22 21:43:41 +0100] [10927] [WARN] Initializing database /tmp/test.aw..
    [2024-01-22 21:43:44 +0100] [10927] [WARN] No admin was found in the database!
    [2024-01-22 21:43:44 +0100] [10927] [WARN] Generated user: 'ansible'
    [2024-01-22 21:43:44 +0100] [10927] [WARN] Generated pwd: '<PASSWORD>'
    [2024-01-22 21:43:44 +0100] [10927] [WARN] Make sure to change the password!
    [2024-01-22 21:43:44 +0100] [10927] [WARN] Starting..
    [2024-01-22 21:43:44 +0100] [10927] [INFO] Starting job-threads
    [2024-01-22 21:43:44 +0100] [10927] [INFO] Listening on http://127.0.0.1:8000

Now you can open the Ansible-WebUI in your browser: `http://localhost:8000 <http://localhost:8000>`_

**Using docker**:

.. code-block:: bash

    # volumes: /data = storage for logs & DB, /play = ansible playbook base-directory
    docker run -d --name ansible-webui --publish 127.0.0.1:8000:8000 --volume $(pwd)/ansible/data:/data --volume $(pwd)/ansible/play:/play ansible-webui:<VERSION>
    # find initial password
    docker logs ansible-webui

----

Proxy
*****

You can find a nginx config example here: `Nginx config example <https://github.com/ansibleguy/ansible-webui/blob/latest/config/nginx.conf>`_

----

Service
*******

You might want to create a service-user:

.. code-block:: bash

    sudo useradd ansible-webui --shell /usr/sbin/nologin --create-home --home-dir /home/ansible-webui


You can find a service config example here: `Systemd config example <https://github.com/ansibleguy/ansible-webui/blob/latest/config/systemd_service.conf>`_

Enabling & starting the service:

.. code-block:: bash

    systemctl enable ansible-webui.service
    systemctl start ansible-webui.service

For production usage you should use a proxy like nginx in from of the Ansible-WebUI webservice!
