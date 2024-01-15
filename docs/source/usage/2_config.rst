==========
2 - Config
==========

Most configuration can be managed using the WebUI: :code:`https://<WEBUI>/a/`

Environmental variables
***********************

* **AW_STATIC**

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
