.. _usage_config:

.. include:: ../_include/head.rst

==========
2 - Config
==========

Most configuration can be managed using the WebUI.

Environmental variables
***********************

* **AW_SERVE_STATIC**

   If defined - the built-in static-file serving is disabled.
   Use this if in production and a `proxy like nginx <https://docs.nginx.com/nginx/admin-guide/web-server/serving-static-content/>`_ is in front of the Ansible-WebUI webservice.


* **AW_DB**

   To define the path where the SQLite3 database is placed.


* **AW_SECRET**

   Define a secret key to use for cookie encryption.
   By default it will be re-generated at service restart.


* **AW_TIMEZONE**

   Override the timezone used.
   Default is the system timezone.


* **AW_ENV**

   Used in development.
   If unset or value is neither 'dev' nor 'staging' the webservice will be in production mode.
   'staging' mode is close to production behavior.

* **AW_DB_MIGRATE**

   Define to disable automatic database schema-upgrades.
   After upgrading the module you might have to run the upgrade manually:

   .. code-block:: bash

       python3 -m ansible-webui.manage makemigrations
       python3 -m ansible-webui.manage makemigrations aw
       python3 -m ansible-webui.manage migrate

* **AW_ADMIN**

   Define the user-name for the initial admin user.

* **AW_ADMIN_PWD**

   Define the password for the initial admin user.

* **AW_PATH_RUN**

   Base directory for Ansible-Runner runtime files. Default: :code:`/tmp/ansible-webui`

* **AW_PATH_PLAY**

   Path to the [Ansible base/playbook directory](https://docs.ansible.com/ansible/2.8/user_guide/playbooks_best_practices.html#directory-layout). Default: current working directory (*when executing ansible-webui*)

* **AW_RUN_TIMEOUT**

   Timeout for the execution of a playbook in seconds. Default: 3600 (1h)

   You might want to lower this value to a sane value for your use-cases.
