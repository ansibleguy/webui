.. _usage_install:

.. include:: ../_include/head.rst

================
1 - Installation
================

Ansible
*******

See `the documentation <https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#pip-install>`_ on how to install Ansible.

**Make sure to read** the `Ansible best-practices <https://docs.ansible.com/ansible/2.8/user_guide/playbooks_best_practices.html#directory-layout>`_ on how to use Ansible!

Install
*******

.. code-block:: bash

    python3 -m pip install ansible-webui

Start
*****

.. code-block:: bash

    # change into your ansible-directory
    cd $PLAYBOOK_DIR

    # foreground
    python3 -m ansible-webui

    # background
    python3 -m ansible-webui > /tmp/aw.log 2> /tmp/aw.err.log &


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

    ExecStart=/usr/bin/python3 -m ansible-webui

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
