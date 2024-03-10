.. _usage_config:

.. include:: ../_include/head.rst

.. include:: ../_include/warn_develop.rst

==========
4 - Config
==========

WebUI
*****

Runtime system configuration can be managed using the WebUI :code:`System - Config` page.

----

Jobs
====

Jobs can be managed at the :code:`Jobs - Manage` page.

**Tip**: The file-browsing also allows you to use your keyboard. Select using Up/Down/Enter keys and auto-complete input using the Tab key!

----

Permissions, Users, Groups
==========================

See: :ref:`Usage - Privileges <usage_permission>`

----

Repositories
============

See: :ref:`Usage - Repositories <usage_repositories>`

----

Environmental variables
***********************

You can find the currently set environmental variables at the :code:`System - Config` page.

----

.. _usage_config_file:

Config File
===========

You are able to provide the following settings by using a `YAML <https://www.redhat.com/en/topics/automation/what-is-yaml>`_ config-file.

* Provide it by flag: :code:`python3 -m ansibleguy-webui -c /etc/ansible-webui/config.yml`

* Provide it by env-var: :code:`AW_CONFIG=/etc/ansible-webui/config.yml`

Example config:

.. code-block:: yaml

    # env-vars without the 'AW_' prefix
    DB: '/etc/ansible-webui/aw.db'
    PORT: 8000
    SECRET: 'sflsjklfdsjlfsDlNDIDEÜNfsnfa-ehöajklsfnn,sf,sdfs,i3uo'
    HOSTNAMES: ['webui.ansibleguy.net', 'cname.webui.ansibleguy.net']
    RUN_TIMEOUT: 600
    SSH_KNOWN_HOSTS: '/etc/ansible-webui/known_hosts'

    AUTH: 'saml'
    SAML:
        METADATA_AUTO_CONF_URL: 'https://<YOUR-IDP>/metadata'
        ...

Docker usage:

.. code-block:: bash

    # safe config to /etc/ansible-webui/config.yml on your host system
    sudo docker run -d ... --env AW_CONFIG=/etc/aw/config.yml --volume /etc/ansible-webui/:/etc/aw/ ansible0guy/webui:latest

----

Settings
========

Only Env
--------

Some settings are only available as environmental variables.

* **AW_SECRET**

   Define a secret key to use for cookie and password encryption.
   By default it will be re-generated at service restart.
   It **has to be set** for job-secrets like passwords to be loadable after restart.
   It has to be **at least 30 characters** long!


* **AW_ADMIN**

   Define the user-name for the initial admin user.


* **AW_ADMIN_PWD**

   Define the password for the initial admin user.


* **AW_PROXY**

   Set if Ansible-WebUI is operated behind a proxy-server.


* **AW_HOSTNAMES**

   Set a comma-separated list of hostnames that are in use and should be trusted. If not set you might encounter 'CSRF' errors.


* **AW_DB**

   Define the path where the SQLite3 database is placed. Default: :code:`${HOME}/.config/ansible-webui/aw.db`


* **AW_PORT**

   Port to listen on. Default: :code:`8000`


* **AW_LISTEN**

   IP Address to listen on. Default: :code:`127.0.0.1`


* **AW_SSL_CERT**

   Optionally provide the path to a ssl certificate to use. Use a (full-)chain if not self-signed.

   **WARNING**: You should use a proxy in front of this application in production setups.


* **AW_SSL_KEY**

   Optionally provide the path to an unencrypted ssl key to use.

   **WARNING**: You should use a proxy in front of this application in production setups.


* **AW_AUTH**

    Choose the authentication mode you want to use.

    One of :code:`saml`, :code:`ldap` or :code:`local`. Default: :code:`local`

    If the mode is set to :code:`saml` or :code:`ldap` - you need to define its config inside the config file.


General System Settings
-----------------------

These settings are also configurable using the WebUI.

* **AW_PATH_LOG**

   Define the path where full job-logs are saved. Default: :code:`${HOME}/.local/share/ansible-webui/`


* **AW_PATH_RUN**

   Base directory for `Ansible-Runner runtime files <https://ansible.readthedocs.io/projects/runner/en/latest/intro/>`_. Default: :code:`/tmp/ansible-webui/`


* **AW_PATH_PLAY**

   Path to the `Ansible base/playbook directory <https://docs.ansible.com/ansible/2.8/user_guide/playbooks_best_practices.html#directory-layout>`_. Default: current working directory (*when executing ansible-webui*)


* **AW_RUN_TIMEOUT**

   Timeout for the execution of a playbook in seconds. Default: 3.600 (1h)
   You might want to lower this value to a sane value for your use-cases.


* **AW_SESSION_TIMEOUT**

   Timeout for WebUI sessions in seconds. Default: 43.200 (12h)


* **AW_SSH_KNOWN_HOSTS**

   Define the path to the known-hosts file that should be used. You can use :code:`${AW_PATH_PLAY}` to reference paths relative to your playbook base-directory!

   Default: None - fallback to user defaults

   Default in docker: :code:`${AW_PATH_PLAY}/known_hosts`


* **AW_TIMEZONE**

   Override the timezone used.
   Default is the system timezone.


Advanced Settings
-----------------

Normal users will not have to use these.

* **AW_SERVE_STATIC**

   If defined - the built-in static-file serving is disabled.
   Use this if in production and a `proxy like nginx <https://docs.nginx.com/nginx/admin-guide/web-server/serving-static-content/>`_ is in front of the Ansible-WebUI webservice.

   Path to serve: :code:`/static/ => ${PATH_VENV}/lib/python${PY_VERSION}/site-packages/ansible-webui/aw/static/`


* **AW_DB_MIGRATE**

   Define to disable automatic database schema-upgrades.
   After upgrading the module you might have to run the upgrade manually:

   .. code-block:: bash

        # if running non-release version
        python3 -m ansibleguy-webui.manage makemigrations
        python3 -m ansibleguy-webui.manage makemigrations aw

        # all
        python3 -m ansibleguy-webui.manage migrate


* **AW_ENV**

   Used in development.
   If unset or value is neither 'dev' nor 'staging' the webservice will be in production mode.
   'staging' mode is close to production behavior.


* **AW_DEBUG**

    Enable debug output.

    This debug mode **SHOULD ONLY BE ENABLED TEMPORARILY**! It could possibly open attack vectors.


* **AW_DOCKER**

   Used to notify the software that it is running inside a docker container. Needed for listen port.

----

Usage
=====

Environmental variables can be set before/when starting Ansible-WebUI.

With basic setup:

.. code-block:: bash

    export AW_SECRET=aaaaaaaaaaaaaaaaaaaaabaaaaaaaaaaaaa
    export AW_PROXY=1
    python3 -m ansibleguy-webui

    # OR

    AW_SECRET=aaaaaaaaaaaaaaaaaaaaabaaaaaaaaaaaaa python3 -m ansibleguy-webui

When using Docker:

.. code-block:: bash

    docker run -d --name ansible-webui --env AW_SECRET=aaaaaaaaaaaaaaaaaaaaabaaaaaaaaaaaaa --env AW_PROXY=1 ...

When running as Systemd service:

.. code-block:: bash

    # add inside the '[Service]' area of the service-config-file
    EnvironmentFile=/etc/ansible-webui/env.txt

    # add variables to the file
    echo 'AW_SECRET=aaaaaaaaaaaaaaaaaaaaabaaaaaaaaaaaaa' >> /etc/ansible-webui/env.txt
    echo 'AW_PROXY=1' >> /etc/ansible-webui/env.txt

    # make sure the access is limited so your secret(s) are safe
    chown root /etc/ansible-webui/env.txt
    chmod 600 /etc/ansible-webui/env.txt
