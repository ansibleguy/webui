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

Demo
****

Check out the demo at: `demo.webui.ansibleguy.net <demo.webui.ansibleguy.net>`_

Login: User :code:`demo`, Password :code:`Ansible1337`

Install
*******

.. code-block:: bash

    python3 -m pip install ansible-webui

**Using docker**:

.. code-block:: bash

    docker image pull ansible0guy/ansible-webui:<VERSION>


Start
*****

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

    docker run -d --name ansible-webui --publish 127.0.0.1:8000:8000 --volume $(pwd)/ansible/data:/data --volume $(pwd)/ansible/play:/play ansible-webui:<VERSION>
    # find initial password
    docker logs ansible-webui


Install Unstable Version
************************

.. code-block:: bash

    # download
    git clone https://github.com/ansibleguy/ansible-webui

    # install dependencies (venv recommended)
    cd ansible-webui
    python3 -m pip install --upgrade requirements.txt
    bash scripts/update_version.sh

    # run
    python3 src/ansible-webui/

**Using docker**:

.. code-block:: bash

    docker image pull ansible0guy/ansible-webui:unstable
    docker run -it --name ansible-webui-dev --publish 127.0.0.1:8000:8000 --volume /tmp/awdata:/data ansible0guy/ansible-webui:unstable

Service
*******

You might want to create a service-user:

.. code-block:: bash

    sudo useradd ansible-webui --shell /usr/sbin/nologin --create-home --home-dir /home/ansible-webui


Without a virtual environment:

.. code-block:: text

    # /etc/systemd/system/ansible-webui.service

    [Unit]
    Description=Ansible WebUI Service
    Documentation=https://ansible-webui.readthedocs.io/
    Documentation=https://github.com/ansibleguy/ansible-webui

    [Service]
    Type=simple
    Environment=LANG="en_US.UTF-8"
    Environment=LC_ALL="en_US.UTF-8"
    Environment=PYTHONUNBUFFERED="1"

    ExecStart=/usr/bin/python3 -m ansible-webui
    ExecReload=/usr/bin/kill -s HUP $MAINPID

    User=ansible-webui
    Group=ansible-webui
    Restart=on-failure
    RestartSec=5s

    StandardOutput=journal
    StandardError=journal
    SyslogIdentifier=ansible-webui

    [Install]
    WantedBy=multi-user.target


When using a virtual environment: (recommended)

.. code-block:: text

    # /etc/systemd/system/ansible-webui.service

    [Unit]
    Description=Ansible WebUI Service
    Documentation=https://ansible-webui.readthedocs.io/
    Documentation=https://github.com/ansibleguy/ansible-webui

    [Service]
    Type=simple
    Environment=LANG="en_US.UTF-8"
    Environment=LC_ALL="en_US.UTF-8"
    Environment=PYTHONUNBUFFERED="1"

    ExecStart=/bin/bash -c 'source /home/ansible-webui/venv/bin/activate \
                            && /usr/bin/python3 -m ansible-webui'

    User=ansible-webui
    Group=ansible-webui
    Restart=on-failure
    RestartSec=5s

    StandardOutput=journal
    StandardError=journal
    SyslogIdentifier=ansible-webui

    [Install]
    WantedBy=multi-user.target

Enabling & starting the service:

.. code-block:: bash

    systemctl enable ansible-webui.service
    systemctl start ansible-webui.service

For production usage you should use a proxy like nginx in from of the Ansible-WebUI webservice!
