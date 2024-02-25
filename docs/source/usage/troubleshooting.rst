.. _usage_troubleshooting:

.. include:: ../_include/head.rst

.. include:: ../_include/warn_develop.rst

.. |ts_sys_ov| image:: ../_static/img/troubleshoot_system_overview.svg
   :class: wiki-img

===============
Troubleshooting
===============

Topology
********

AnsibleGuy WebUI is made of a few main components.

It will be beneficial for the troubleshooting process if we find out in which the error occurs.

|ts_sys_ov|

----

Debugging
*********

You can enable the debug mode at the :code:`System - Config` page.

If that is not possible you can alternatively set the :code:`AW_ENV` environmental variable to :code:`dev`.

This debug mode **SHOULD ONLY BE ENABLED TEMPORARILY**! It could possibly open attack vectors.

You might need to restart the application to apply this setting.

----

Versions
********

You can find the versions of software packages in use at the :code:`System - Environment` page.

Alternatively you can check it from the cli: :code:`python3 -m ansibleguy-webui.cli --version`

----

Job Execution
*************

If you want to troubleshoot a job execution, you will have to find out if it is an issue with Ansible or the WebUI system.

The Ansible execution itself can fail because of some common issues:

* Unable to connect

  * Network issue
  * Wrong credentials supplied
  * Target system is mis-configured

* Controller dependencies

  * Ansible needs Python Modules and in some cases Ansible Collections and Ansible Roles to function correctly

    These need to be installed and should be up-to-date.

    You can find the current versions used by your Controller system at the :code:`System - Environment` page

  * If you are using Docker - you can install those dependencies using requirements-files. See :ref:`Usage - Docker <usage_docker>`

* to be continued..

----

Common Issues
*************

----

SSH Hostkey Verification
========================

**Error**: While executing Ansible you see: :code:`Host key verification failed`

**Problem**:

* SSH has a security feature that should keep you safe from `man-in-the-middle attacks <https://en.wikipedia.org/wiki/Man-in-the-middle_attack>`_ which could allow the attacker to take over your SSH account/credentials.

  See also: `Ansible Docs - Hostkey Verification <https://docs.ansible.com/ansible/latest/inventory_guide/connection_details.html>`_

* As this security feature is important you **SHOULD NOT DISABLE IT IN PRODUCTION** by adding the environmental variable `ANSIBLE_HOST_KEY_CHECKING=False` to your jobs!

* In production you might want to either:

  * Maintain a `list of known-good hostkeys <https://en.wikibooks.org/wiki/OpenSSH/Client_Configuration_Files#~/.ssh/known_hosts>`_

    You can specify which :code:`known_hosts` file AnsibleGuy WebUI should use, using the config setting :code:`AW_SSH_KNOWN_HOSTS`

  * Implement `CA signed-hostkeys <https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/6/html/deployment_guide/sec-creating_ssh_ca_certificate_signing-keys>`_


----

Python Module not installed
===========================

**Error**: While executing Ansible you see: :code:`No module named '<MODULE>'`

**Problem**:

* Your Ansible controller system is missing a required Python3 module!

* If you are NOT using Docker, you can install it manually using PIP: :code:`python3 -m pip install <MODULE>`

  You could also find and install the module using your systems package manager: :code:`sudo apt install python3-<MODULE>` (NOTE: these packages are older versions)

* If you are using Docker, you can create and mount a :code:`requirements.txt` and restart your container. See also: :ref:`Usage - Docker <usage_docker>`

----

Connection in use
=================

**Error**: While starting AW you see: :code:`Connection in use: ('127.0.0.1', 8000)`

**Problem**

* Make sure no other process is binding to port 8000: :code:`netstat -tulpn | grep 8000`

* The app failed last time. There is still an old process running. If this happens repeatedly - open an issue!

  You can find and kill it:

  .. code-block:: bash

      # find it
      pgrep -f ansibleguy-webui
      netstat -tulpn | grep 8000
      ps -aux | grep ansibleguy-webui | grep -v grep

      # kill it
      pkill -f ansibleguy-webui
      kill -9 <PID>

----

Database is locked
==================

**Error**: The Web interface shows a plain :code:`Error 500` and the console shows :code:`django.db.utils.OperationalError: database is locked`

**Problem**:

* I've encountered this issue a few times. It occurs because the `SQLite database is locked by a write-operation <https://github.com/ansibleguy/webui/issues/6>`_.

  Restarting the application is the easiest way of working around it.

  If it occurs more often - please open an issue!

* If you are running many jobs - you could try to keep a minute between their scheduled executions.
