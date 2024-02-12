.. _usage_permission:

.. include:: ../_include/head.rst

.. include:: ../_include/warn_develop.rst

.. |perm_users_groups| image:: ../_static/img/permission_users_groups.png
   :class: wiki-img

.. |perm_ui| image:: ../_static/img/permission_ui.png
   :class: wiki-img

.. |perm_overview| image:: ../_static/img/permission_overview.svg
   :class: wiki-img

==========
Privileges
==========

You can set job-permissions to limit user actions.

Users & Groups
**************

The :code:`System - Admin - Users/Groups` admin-page allows you to create new users and manage group memberships.

To allow a user to create jobs, permissions and global-credentials you need to activate the :code:`Staff status`.

|perm_users_groups|

----

Permissions
***********

The UI at :code:`Settings - Permissions` allows you to create job & credential permissions and link them to users and groups.

|perm_ui|

Each job & credential can have multiple permissions linked to it.

**Permission types:**

* **Read** - only allow user to read job and job-logs
* **Execute** - allow user to start & stop the job + 'Read'
* **Write** - allow user to modify the job + 'Execute'
* **Full** - allow user to delete the job + 'Write'

|perm_overview|
