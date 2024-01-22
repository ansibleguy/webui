.. _usage_api:

.. include:: ../_include/head.rst

.. include:: ../_include/warn_develop.rst

.. |api_docs| image:: ../_static/img/config_admin.png
   :class: wiki-img


===
API
===

This project has a API first development approach!

To use the API you have to create an API key: `ui/settings/api_keys <http://localhost:8000/ui/settings/api_keys>`_


Examples
********

Requests must have the API key set in the :code:`X-Api-Key` header.

.. code-block:: bash

    # list own api keys
    curl -X 'GET' 'http://localhost:8000/api/key' -H 'accept: application/json' -H "X-Api-Key: <KEY>"
    > {"tokens":["ansible-2024-01-20-16-50-51","ansible-2024-01-20-16-10-42"]}

    # list jobs
    curl -X 'GET' 'http://localhost:8000/api/job' -H 'accept: application/json' -H "X-Api-Key: <KEY>"
    > [{"id":34,"name":"Deploy App","inventory":"inventories/dev/hosts.yml","playbook":"app.yml","schedule":"22 14 * * 4,5","limit":"dev1,dev3","verbosity":0,"comment":"Deploy my app to the first two development servers","environment_vars":"MY_APP_ENV=DEV,TZ=UTC"}]

    # execute job
    curl -X 'POST' 'http://localhost:8000/api/job/34' -H 'accept: application/json' -H "X-Api-Key: lEfPOA2o.g71oIrgkwChIfEBrRdK6NvjXrYMlVIcZ"
    > {"msg":"Job 'Deploy App' execution queued"}

API Docs
********

You can see the available API-endpoints in the built-in API-docs: `ui/api_docs <http://localhost:8000/ui/api_docs>`_ (*swagger*)

|api_docs|
