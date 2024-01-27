.. _usage_security:

.. include:: ../_include/head.rst

.. include:: ../_include/warn_develop.rst


========
Security
========

Ansible needs to handle sensible secrets like administrative passwords to function.

That's why it is very important to keep security in our mind.

You are very welcome to search for security vulnerabilities and `report them <https://github.com/ansibleguy/ansible-webui/issues>`_!


Features
********

Security considerations this project does take into account:

* The encryption key is randomized at startup by default - if none was provided by the user.

* The encryption key has to be at least 30 characters long

* Job secrets like passwords are stored encrypted (*AES256-CBC*)

* Job secrets are not passed as commandline-arguments but written to files:

    Example:

    .. code-block:: bash

        [INFO] [play] Running job 'test': 'ansible-playbook --become-password-file /tmp/ansible-webui/2024-01-26_21-14-0066101/.aw_become_pass --vault-password-file /tmp/ansible-webui/2024-01-26_21-14-0066101/.aw_vault_pass -i inventory/hosts.yml --limit myHost playbook1.yml'

    These files are:

    * .. created with mode 0600

    * .. overwritten and deleted at execution-cleanup

* Usage of GitHub's `dependabot <https://docs.github.com/en/code-security/supply-chain-security/understanding-your-software-supply-chain/about-supply-chain-security#what-is-dependabot>`_ and `CodeQL <https://docs.github.com/code-security/code-scanning/automatically-scanning-your-code-for-vulnerabilities-and-errors/about-code-scanning-with-codeql>`_

Setup
*****

* You should use a proxy like nginx in front of Ansible-WebUI

    You should: (*example config will be added later on*)

    * .. use HTTPS

    * .. restrict the HTTP security headers (X-Frame-Options, X-Content-Type, Content-Security-Policy and Referrer-Policy, HSTS)

    * .. limit the networks able to access the Web-application using your firewall(s)

    * .. `limit the request rate <https://docs.nginx.com/nginx/admin-guide/security-controls/controlling-access-proxied-http/>`_ on the login form :code:`/a/*` and API :code:`/api/*`

* Make sure the Account passwords and API keys are kept/used safe
