.. _usage_repositories:

.. include:: ../_include/head.rst

.. include:: ../_include/warn_develop.rst

.. |repo_ui| image:: ../_static/img/repo_ui.png
   :class: wiki-img


============
Repositories
============

By default the static Repository set by :code:`AW_PATH_PLAY` is used.

You are able to create multiple Repositories that act as Ansible-Playbook base-directories.

|repo_ui|

----

Static
******

Absolute path to an existing local static directory that contains your `playbook directory structure <https://docs.ansible.com/ansible/2.8/user_guide/playbooks_best_practices.html#directory-layout>`_.

----

Git
***

Git repositories are also supported.

They can either be updated at execution or completely re-created (*isolated*).

The timeout for any single git-command is 5min.

----

Override commands
=================

If you have some special environment or want to tweak the way your repository is cloned - you can override the default git-commands!

Default commands:

**Create**

.. code-block:: bash

    git clone --branch ${BRANCH} (--depth ${DEPTH}) ${ORIGIN}
    # if LFS is enabled
    git lfs fetch
    git lfs checkout

**Update**

.. code-block:: bash

    git reset --hard
    git pull (--depth ${DEPTH})
    # if LFS is enabled
    git lfs fetch
    git lfs checkout

----

Hook commands
=============

You are able to run some hook-commands before and after updating the repository.

If you want to run multiple ones - they need to be comma-separated.

These hooks will not be processed if you override the actual create/update command.

----

Clone via SSH
=============

You can specify which :code:`known_hosts` file AW should use using the :ref:`System config <usage_config>`!

You are able to append the port to the origin string like so: :code:`git@git.intern -p1337`

The SSH-key configured in the linked credentials will be used.
