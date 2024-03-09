.. _usage_auth:

.. include:: ../_include/head.rst

.. include:: ../_include/warn_develop.rst

==============
Authentication
==============

SAML SSO
********

**Tested config examples**: `Google Workspace <https://github.com/ansibleguy/webui/blob/latest/examples/saml_google_workspace.yml>`_

This app is integrating the `grafana/django-saml2-auth module <https://github.com/grafana/django-saml2-auth>`_ (indirect `pysaml2 <https://github.com/IdentityPython/pysaml2>`_).

To enable it:

1. Set the **AW_AUTH** env-var to :code:`saml`

2. Create a `YAML config file <https://www.redhat.com/en/topics/automation/what-is-yaml>`_ to configure the SAML settings you need.

  For options see: `Module settings <https://github.com/grafana/django-saml2-auth?tab=readme-ov-file#module-settings>`_

  Example:

  .. code-block:: yaml

      ---

      # config file at '/etc/ansible-webui/saml.yml'

      METADATA_AUTO_CONF_URL: 'https://<YOUR-IDP>/metadata'
      # METADATA_LOCAL_FILE_PATH: '/etc/ansible-webui/saml-metadata.txt'

      # replace with your scheme, domain and port!
      ASSERTION_URL: 'http://localhost:8000'
      ENTITY_ID: 'http://localhost:8000/a/saml/acs/'
      DEFAULT_NEXT_URL: 'http://localhost:8000/'

      CREATE_USER: true
      NEW_USER_PROFILE:
          USER_GROUPS: []  # The default group name when a new user logs in
          ACTIVE_STATUS: true
          STAFF_STATUS: true  # allow user to view 'System - Admin' page
          SUPERUSER_STATUS: false  # full system admin privileges

      ATTRIBUTES_MAP:  # email or username and token are required!
          # mapping: django => IDP
          email: 'email'
          username: 'lastName'
          token: 'id'
          # optional:
          first_name: 'user.first_name'
          last_name: 'user.last_name'
          groups: 'Groups'  # Optional

      DEBUG: false  # DO NOT PERMANENTLY ENABLE!

      GROUPS_MAP:  # map IDP groups to django groups
          'IDP GROUP': 'AW Job Managers'

      # NAME_ID_FORMAT: 'user.email'
      # KEY_FILE: '/etc/ansible-webui/saml.key'
      # CERT_FILE: '/etc/ansible-webui/saml.crt'

3. Set the **AW_SAML_CONFIG** env-var containing the absolute path to your config-file (*readable by the user executing AW*)

4. SSO identity provider settings:

  **ACS URL**: :code:`http://localhost:8000/a/saml/acs/`

  **Entity ID/Audience URL**: :code:`http://localhost:8000/a/saml/acs/`

  Note: Replace *http://localhost:8000* with your scheme, domain and port


5. For non-Docker setups: Install the :code:`xmlsec` package that is used internally (see: `details <https://github.com/IdentityPython/pysaml2?tab=readme-ov-file#external-dependencies>`_)

You should now be able to see :code:`[INFO] [main] Using Auth-Mode: saml` logged on startup.

If you have troubles with getting SAML to work - check out :ref:`Usage - Troubleshooting - SAML <usage_troubleshooting_saml>`
