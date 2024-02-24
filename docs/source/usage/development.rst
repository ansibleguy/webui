.. _usage_development:

.. include:: ../_include/head.rst

.. include:: ../_include/warn_develop.rst

===========
Development
===========

Feel free to contribute to this project using `pull-requests <https://github.com/ansibleguy/webui/pulls>`_, `issues <https://github.com/ansibleguy/webui/issues>`_ and `discussions <https://github.com/ansibleguy/webui/discussions>`_!

Testers are also very welcome! Please `give feedback <https://github.com/ansibleguy/webui/issues>`_

For further details - see: `Contribute <https://github.com/ansibleguy/webui/blob/latest/CONTRIBUTE.md>`_

Read into the :ref:`Troubleshooting Guide <usage_troubleshooting>` to get some insight on how the stack works.


----

Install Unstable Version
************************

**WARNING**: If you run non-release versions you will have to save you :code:`src/ansibleguy-webui/aw/migrations/*` else your database upgrades might fail. Can be ignored if you do not care about losing the Ansible-WebUI config.

.. code-block:: bash

    # download
    git clone https://github.com/ansibleguy/webui

    # install dependencies (venv recommended)
    cd ansible-webui
    python3 -m pip install --upgrade requirements.txt
    bash scripts/update_version.sh

    # run
    python3 src/ansibleguy-webui/


**Using docker**:

.. code-block:: bash

    docker image pull ansible0guy/webui:unstable
    docker run -it --name ansible-webui-dev --publish 127.0.0.1:8000:8000 --volume /tmp/awdata:/data ansible0guy/webui:unstable
    # to safe db-migrations use:
    # --volume /var/local/ansible-webui/migrations/:/usr/local/lib/python3.10/site-packages/ansible-webui/aw/migrations
