.. _usage_api:

.. include:: ../_include/head.rst

.. include:: ../_include/warn_develop.rst

===
API
===

To use the API you have to create an API key: `ui/settings/api_keys <http://localhost:8000/ui/settings/api_keys>`_

You can see the available API-endpoints in the built-in API-docs: `ui/api_docs <http://localhost:8000/ui/api_docs>`_ (*swagger*)

Requests must have the API key set in the :code:`X-Api-Key` header.

Examples
********

.. code-block:: bash

    # add another api key
    curl -X 'POST' 'http://localhost:8000/api/key' -H 'accept: application/json' -H "X-Api-Key: <KEY>"
    > {"token":"ansible-2024-01-20-16-50-51","key":"r6yTsF9G.9qOt8ivfvFbpIkBh228tgAZjaNtnmDpw"}

    # list own api keys
    curl -X 'GET' 'http://localhost:8000/api/key' -H 'accept: application/json' -H "X-Api-Key: <KEY>"
    > {"tokens":["ansible-2024-01-20-16-50-51","ansible-2024-01-20-16-10-42"]}
