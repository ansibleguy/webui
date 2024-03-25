.. _usage_security:

.. include:: ../_include/head.rst

.. include:: ../_include/warn_develop.rst


========
Security
========

Ansible needs to handle sensible secrets like administrative passwords to function.

That's why it is very important to keep security in our mind.

You are very welcome to search for security vulnerabilities and `report them <https://github.com/ansibleguy/webui/issues>`_!

----

.. _usage_security_issues:

Known Issues
************

* **Remote-Code-Execution on Controller**

  As mentioned in `this issue <https://github.com/ansibleguy/webui/issues/33>`_ the Ansible-Execution is done in the same context as the Web-Service.

  So you should be aware that every user that can supply the Web-Service with playbooks, or execute ad-hoc commands, is able to execute code in the context of the service-user.

  This **includes reading the config-file**!

  So if possible - you should set your **AW_SECRET** (*and other secrets*) as environmental variable!

  **Possible future fixes**:

  * Run Ansible-Runner with `process-isolation (execution in container) <https://ansible.readthedocs.io/projects/runner/en/stable/standalone/#running-with-process-isolation>`_ enabled (*not yet implemented in AW*)

  * Run Ansible-Runner as `dedicated user <https://github.com/ansible/ansible-runner/issues/1350>`_ (*not yet implemented in Ansible-Runner and AW*)

----

Features
********

Security considerations this project does take into account:

* The encryption key is randomized at startup by default - if none was provided by the user.

* The encryption key has to be at least 30 characters long

* Job secrets like passwords are stored encrypted (*AES256-CBC*)

* Job secrets like passwords are never returned to the user/Web-UI

* Job secrets are not passed as commandline-arguments but written to files:

    Example:

    .. code-block:: bash

        [INFO] [play] Running job 'test': 'ansible-playbook --become-password-file /tmp/ansible-webui/2024-01-26_21-14-0066101/.aw_become_pass --vault-password-file /tmp/ansible-webui/2024-01-26_21-14-0066101/.aw_vault_pass -i inventory/hosts.yml --limit myHost playbook1.yml'

    These files are:

    * created with mode 0600

    * overwritten and deleted at execution-cleanup

* Usage of GitHub's `dependabot <https://docs.github.com/en/code-security/supply-chain-security/understanding-your-software-supply-chain/about-supply-chain-security#what-is-dependabot>`_ and `CodeQL <https://docs.github.com/code-security/code-scanning/automatically-scanning-your-code-for-vulnerabilities-and-errors/about-code-scanning-with-codeql>`_

Setup
*****

* You should use a proxy like nginx in front of AW

    Recommended Config: (`Example <https://github.com/ansibleguy/webui/blob/latest/examples/nginx.conf>`_)

    * use HTTPS with a valid certificate

    * restrict the HTTP security headers (X-Frame-Options, X-Content-Type, Content-Security-Policy and Referrer-Policy, HSTS)

    * limit the networks able to access the Web-application using your firewall(s)

    * limit the `request rate <https://docs.nginx.com/nginx/admin-guide/security-controls/controlling-access-proxied-http/>`_ on the login form :code:`/a/*` and API :code:`/api/*`

    * serve static files using the proxy

        :code:`/static/ => ${PATH_VENV}/lib/python${PY_VERSION}/site-packages/ansible-webui/aw/static/`

* Make sure the Account passwords and API keys are kept/used safe
